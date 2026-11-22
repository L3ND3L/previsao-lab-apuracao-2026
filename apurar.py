"""Apuração portátil, sem modelo de IA, chaves de API ou dependências externas."""
from datetime import datetime, timezone
import argparse
import hashlib
import json
import math
from pathlib import Path
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parent
KEYS = ['zero','one','two_plus']
NAMES = {'single_agent':'Agente único','multi_initial':'Grupo antes da revisão',
         'multi_revised':'Grupo após revisão','poisson_reference':'Referência matemática'}
UTC = timezone.utc

def date(value):
    dt = datetime.fromisoformat(value.replace('Z','+00:00'))
    if dt.tzinfo is None:
        raise ValueError('Data sem fuso.')
    return dt.astimezone(UTC)

def iso(dt):
    return dt.astimezone(UTC).isoformat().replace('+00:00','Z')

def digest(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f,'sha256').hexdigest()

def encoded(obj):
    return (json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+'\n').encode('utf-8')

def save(path,content):
    with path.open('xb') as f:
        f.write(content)

def brier(p,winner):
    if len(p)!=3 or any(type(v) not in (int,float) or not math.isfinite(v) or not 0<=v<=1 for v in p) or abs(sum(p)-1)>1e-8:
        raise ValueError('Distribuição inválida.')
    return sum((v-int(i==winner))**2 for i,v in enumerate(p))

def load():
    actual = digest(ROOT/'dados.json')
    if actual!=(ROOT/'dados.sha256').read_text(encoding='ascii').strip():
        raise ValueError('Hash dos dados não confere.')
    d = json.loads((ROOT/'dados.json').read_bytes())
    if d['scenario_order']!=KEYS or d['cost_limit_brl']!=0:
        raise ValueError('Configuração inesperada.')
    for p in d['forecasts'].values():
        brier(p,0)
    e = d['event']
    if not date(d['cutoff_utc'])<date(d['committed_at_utc'])<date(e['start_utc'])<date(e['end_utc_exclusive'])<date(e['resolution_not_before_utc'])<date(e['resolution_deadline_utc']):
        raise ValueError('Cronologia inválida.')
    if e['min_magnitude']!=5.5:
        raise ValueError('Magnitude inesperada.')
    return d

def check_window(event,when):
    if not date(event['resolution_not_before_utc'])<=when<date(event['resolution_deadline_utc']):
        raise ValueError('Fora da janela registrada; não consultar nem pontuar.')

def fetch(event):
    params={'format':'geojson','starttime':event['start_utc'],'endtime':event['end_utc_exclusive'],
        'minmagnitude':event['min_magnitude'],'eventtype':'earthquake','orderby':'time-asc','limit':20000,'nodata':204}
    url='https://earthquake.usgs.gov/fdsnws/event/1/query?'+urllib.parse.urlencode(params)
    req=urllib.request.Request(url,headers={'User-Agent':'previsao-lab-cloud/1','Accept':'application/json'})
    with urllib.request.urlopen(req,timeout=60) as r:
        if urllib.parse.urlparse(r.url).hostname!='earthquake.usgs.gov':
            raise ValueError('Redirecionamento inesperado.')
        raw=r.read(16_000_001)
        if len(raw)>16_000_000:
            raise ValueError('Resposta excedeu o limite.')
        return raw,{'url':url,'http_status':r.status,'http_date':r.headers.get('Date'),
            'received_at_utc':iso(datetime.now(UTC))}

def count_events(raw,meta,event):
    if meta['http_status']==204 and not raw:
        return []
    doc=json.loads(raw)
    m=doc.get('metadata',{})
    features=doc.get('features',[])
    cutoff=date(meta['received_at_utc']).timestamp()*1000
    if doc.get('type')!='FeatureCollection' or m.get('status')!=200 or type(m.get('generated')) not in (int,float) or not math.isfinite(m['generated']) or m['generated']>cutoff:
        raise ValueError('Fonte inválida ou posterior à coleta.')
    if len(features)>=20000 or (m.get('count') is not None and m['count']!=len(features)):
        raise ValueError('Catálogo possivelmente incompleto.')
    ids,seen=[],set()
    start=date(event['start_utc']).timestamp()*1000
    end=date(event['end_utc_exclusive']).timestamp()*1000
    for f in features:
        if f['id'] in seen:
            raise ValueError('ID duplicado.')
        seen.add(f['id'])
        p=f['properties']
        if p.get('type')!='earthquake':
            continue
        t,u,mag=p.get('time'),p.get('updated'),p.get('mag')
        if any(type(v) not in (int,float) or not math.isfinite(v) for v in (t,u,mag)):
            raise ValueError('Evento sem campos verificáveis.')
        if start<=t<end and u<=cutoff and mag>=event['min_magnitude']:
            ids.append(f['id'])
    return ids

def resolve(data,dest):
    check_window(data['event'],datetime.now(UTC))
    if dest.exists():
        # Reexecuções não podem buscar um catálogo mais favorável nem substituir resultados.
        raise FileExistsError('Apuração já existente; recusada nova coleta.')
    raw,meta=fetch(data['event'])
    check_window(data['event'],date(meta['received_at_utc']))
    ids=count_events(raw,meta,data['event'])
    winner=min(len(ids),2)
    scores={name:brier(p,winner) for name,p in data['forecasts'].items()}
    delta=scores['multi_revised']-scores['single_agent']
    comparison='Grupo pontuou melhor' if delta<0 else 'Agente único pontuou melhor' if delta>0 else 'Empate'
    result={'run_id':data['run_id'],'observed_count':len(ids),'winner':KEYS[winner],
        'event_ids':ids,'source':meta,'brier_multiclass_sum':scores,'multi_minus_single':delta,
        'comparison':comparison,'original_manifest_sha256':data['original_manifest_sha256'],
        'original_forecast_sha256':data['original_forecast_sha256'],'exported_data_sha256':digest(ROOT/'dados.json')}
    rows='\n'.join(f'| {NAMES[name]} | '+' | '.join(f'{100*p:.2f}%' for p in data['forecasts'][name])+f' | {scores[name]:.6f} |' for name in NAMES)
    report=f'''# Apuração do laboratório de previsão

**{comparison} neste evento.**

Contagem observada: {len(ids)} terremotos M ≥ 5,5 no mundo, por horário de origem na janela registrada.
Cenário ocorrido: {['nenhum','exatamente um','dois ou mais'][winner]}.

| Método | Nenhum | Um | Dois ou mais | Brier |
|---|---:|---:|---:|---:|
{rows}

Brier usa a convenção de soma, entre 0 e 2; menor é melhor.
Diferença grupo após revisão menos agente único: {delta:.6f}.

Um evento não demonstra superioridade nem calibração. O grupo usou seis chamadas contra uma do agente único.
As probabilidades foram preservadas e não vêm de frequências de simulações.

Coleta: {meta['received_at_utc']}. Resultado segundo a primeira captura bem-sucedida nesta instalação, dentro da janela original de apuração. Revisões posteriores não substituem este resultado.

Fonte: [Catálogo USGS]({meta['url']}). Resposta original em `fonte-usgs.bin`.
Manifesto original: `{data['original_manifest_sha256']}`.
SHA256 da cópia mínima: `{digest(ROOT/'dados.json')}`.
'''
    dest.mkdir()
    save(dest/'fonte-usgs.bin',raw)
    save(dest/'resultado.json',encoded(result))
    save(dest/'relatorio.md',report.encode('utf-8'))
    save(dest/'manifesto.json',encoded({p.name:digest(p) for p in sorted(dest.iterdir()) if p.is_file()}))
    print(report)
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verificar',action='store_true',help='Conferir dados sem consultar resultados.')
    args=parser.parse_args()
    data=load()
    if args.verificar:
        print('Dados e cronologia conferidos. Nenhuma consulta de resultado feita.')
    else:
        resolve(data,ROOT/'resultados')

if __name__=='__main__':
    main()
