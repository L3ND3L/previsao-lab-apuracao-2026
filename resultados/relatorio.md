# Apuração do laboratório de previsão

**Grupo pontuou melhor neste evento.**

Contagem observada: 2 terremotos M ≥ 5,5 no mundo, por horário de origem na janela registrada.
Cenário ocorrido: dois ou mais.

| Método | Nenhum | Um | Dois ou mais | Brier |
|---|---:|---:|---:|---:|
| Agente único | 57.14% | 7.14% | 35.71% | 0.744898 |
| Grupo antes da revisão | 53.33% | 33.33% | 13.33% | 1.146667 |
| Grupo após revisão | 40.00% | 23.33% | 36.67% | 0.615556 |
| Referência matemática | 18.27% | 31.06% | 50.68% | 0.373113 |

Brier usa a convenção de soma, entre 0 e 2; menor é melhor.
Diferença grupo após revisão menos agente único: -0.129342.

Um evento não demonstra superioridade nem calibração. O grupo usou seis chamadas contra uma do agente único.
As probabilidades foram preservadas e não vêm de frequências de simulações.

Coleta: 2026-11-27T01:00:22.583077Z. Resultado segundo a primeira captura bem-sucedida nesta instalação, dentro da janela original de apuração. Revisões posteriores não substituem este resultado.

Fonte: [Catálogo USGS](https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=2026-11-23T00%3A00%3A00.000000Z&endtime=2026-11-24T00%3A00%3A00.000000Z&minmagnitude=5.5&eventtype=earthquake&orderby=time-asc&limit=20000&nodata=204). Resposta original em `fonte-usgs.bin`.
Manifesto original: `d048d70d9800f92257bf93f07c88ca5f877e0b07775903c409c9bceb48851961`.
SHA256 da cópia mínima: `fe1fca38c19a17828b8fdc841d3f3c28877df98ba5715ab063385102224449a6`.
