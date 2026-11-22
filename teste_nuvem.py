"""Exemplos sintéticos; nunca consultam o resultado futuro."""
from datetime import datetime,timedelta,timezone
from pathlib import Path
from contextlib import redirect_stdout
from io import StringIO
import tempfile
import unittest
from unittest.mock import patch
import apurar

T=datetime(2026,11,23,tzinfo=timezone.utc)
E={'start_utc':apurar.iso(T),'end_utc_exclusive':apurar.iso(T+timedelta(days=1)),
   'resolution_not_before_utc':apurar.iso(T+timedelta(days=4)),
   'resolution_deadline_utc':apurar.iso(T+timedelta(days=5)),'min_magnitude':5.5}
META={'http_status':200,'received_at_utc':apurar.iso(T+timedelta(days=4)),
      'url':'https://example.invalid/fonte-sintetica'}

def feature(id,hours=0,mag=5.5):
    return {'id':id,'properties':{'type':'earthquake','time':(T+timedelta(hours=hours)).timestamp()*1000,
        'updated':(T+timedelta(hours=hours)).timestamp()*1000,'mag':mag}}

def doc(items):
    return apurar.encoded({'type':'FeatureCollection','metadata':{'status':200,'count':len(items),
        'generated':(T+timedelta(days=4)).timestamp()*1000},'features':items})

class Teste(unittest.TestCase):
    def test_dados_congelados(self):
        data=apurar.load()
        self.assertEqual(data['original_manifest_sha256'],'d048d70d9800f92257bf93f07c88ca5f877e0b07775903c409c9bceb48851961')

    def test_brier(self):
        self.assertEqual(apurar.brier([1,0,0],0),0)
        self.assertEqual(apurar.brier([1,0,0],1),2)
        self.assertAlmostEqual(apurar.brier([.1,.2,.7],2),.14)
        for bad in ([.5,.5,.5],[float('nan'),0,1],[True,0,0]):
            with self.assertRaises(ValueError): apurar.brier(bad,0)

    def test_janela(self):
        for dt in (T+timedelta(days=4)-timedelta(microseconds=1),T+timedelta(days=5)):
            with self.assertRaises(ValueError): apurar.check_window(E,dt)
        apurar.check_window(E,T+timedelta(days=4))

    def test_limites_e_magnitude(self):
        items=[feature('inicio'),feature('fim',24),feature('menor',3,5.4),feature('segundo',23)]
        self.assertEqual(apurar.count_events(doc(items),META,E),['inicio','segundo'])

    def test_duplicado(self):
        with self.assertRaises(ValueError): apurar.count_events(doc([feature('a'),feature('a')]),META,E)

    def test_vazio_e_http204(self):
        self.assertEqual(apurar.count_events(doc([]),META,E),[])
        self.assertEqual(apurar.count_events(b'',dict(META,http_status=204),E),[])

    def test_fonte_futura(self):
        import json
        source=json.loads(doc([]))
        source['metadata']['generated']+=1000
        with self.assertRaises(ValueError): apurar.count_events(apurar.encoded(source),META,E)

    def test_fluxo_sintetico_sem_sobrescrita(self):
        data=apurar.load()
        data['event']=E
        class Clock(datetime):
            @classmethod
            def now(cls,tz=None): return T+timedelta(days=4)
        with tempfile.TemporaryDirectory() as temp, patch.object(apurar,'datetime',Clock), patch.object(apurar,'fetch',return_value=(doc([feature('a'),feature('b',1)]),META)) as network:
            dest=Path(temp)/'resultados'
            # O relatório fictício não deve parecer uma apuração real nos logs.
            with redirect_stdout(StringIO()):
                result=apurar.resolve(data,dest)
            self.assertEqual(result['observed_count'],2)
            self.assertEqual(result['winner'],'two_plus')
            self.assertEqual(result['brier_multiclass_sum']['single_agent'],apurar.brier(data['forecasts']['single_agent'],2))
            self.assertTrue((dest/'fonte-usgs.bin').exists())
            with self.assertRaises(FileExistsError): apurar.resolve(data,dest)
            self.assertEqual(network.call_count,1)

    def test_antecipada_sem_rede(self):
        data=apurar.load()
        data['event']=E
        class Clock(datetime):
            @classmethod
            def now(cls,tz=None): return T
        with patch.object(apurar,'datetime',Clock),patch.object(apurar,'fetch') as network:
            with self.assertRaises(ValueError): apurar.resolve(data,Path('resultado-nao-criado'))
            network.assert_not_called()

if __name__=='__main__':
    unittest.main(verbosity=2)
