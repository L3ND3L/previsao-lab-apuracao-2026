# Laboratório de previsão — apuração na nuvem

Este repositório contém a cópia mínima de uma previsão registrada antes do evento e um programa para conferir o resultado público. Não executa modelos de IA e não usa APIs pagas.

**Apuração agendada:** 26/11/2026 às 21h de Brasília, equivalente a 27/11/2026 00h UTC. O computador do proprietário pode ficar desligado. O GitHub pode atrasar ou deixar de disparar uma execução agendada; o início no minuto exato não é garantido.

## Como acompanhar

- [Execuções e validação na nuvem](https://github.com/L3ND3L/previsao-lab-apuracao-2026/actions)
- [Avisos de conclusão ou falha](https://github.com/L3ND3L/previsao-lab-apuracao-2026/issues)
- Após a apuração, a pasta `resultados` conterá o relatório, as pontuações, os dados originais do USGS e um manifesto de integridade.

A notificação será feita por um aviso no GitHub mencionando o proprietário. E-mail depende das configurações de notificações da conta. Não há envio automático para a conversa original no Codex.

## O experimento

Pergunta: quantos terremotos de magnitude preferencial pelo menos 5,5 constarão no catálogo USGS com horário de origem de **22/11/2026 às 21h até antes de 23/11/2026 às 21h**, em Brasília?

São três cenários: nenhum, exatamente um e dois ou mais. Comparamos o agente único, o grupo antes e depois da revisão e uma referência matemática simples. As probabilidades já foram registradas e não são recalculadas nesta apuração. São estimativas experimentais não calibradas, sem conversão de frequências de simulações em probabilidades reais.

O resultado segue a primeira captura bem-sucedida por esta instalação dentro da janela original de apuração: **de 26/11/2026 às 21h até antes de 27/11/2026 às 21h**, em Brasília. Usamos IDs únicos de terremotos, magnitude preferencial ≥ 5,5 e intervalo de origem com início incluído e fim excluído. Revisões posteriores não substituem a captura original.

A pontuação é Brier multiclasse na convenção de soma: de 0 a 2, menor é melhor. Uma diferença negativa de `multi_minus_single` favorece o grupo depois da revisão naquele evento. Um evento não prova superioridade nem calibração. O grupo usou seis chamadas de IA contra uma do agente único, com orçamento desigual.

## Validação e segurança do registro

Cada publicação na branch principal roda uma verificação dos hashes, nove testes com exemplos sintéticos e uma consulta ao endpoint de versão do USGS, sem consultar resultados de terremotos. Essas verificações não produzem uma apuração real. O modo manual padrão também é somente verificar.

Somente o horário agendado ou a escolha manual explícita de apurar acionam a consulta de resultados. O programa bloqueia consultas fora da janela e recusa sobrescrever uma apuração existente. Após a tentativa agendada, o próprio fluxo se desativa para não repetir no ano seguinte. Uma execução manual dentro da janela pode ser usada para tratar uma falha de consulta.

O registro completo original permanece local. Sua integridade foi conferida antes da exportação. Este repositório contém os hashes de referência, mas não todos os arquivos originais; auditoria integral da relação entre a cópia e o original exige esses arquivos locais. A publicação cria um histórico externo desta cópia mínima, mas não é uma certificação de imutabilidade.

Manifesto original: `d048d70d9800f92257bf93f07c88ca5f877e0b07775903c409c9bceb48851961`.

O repositório é público. Contém apenas previsões, regras, hashes, código e resultados públicos. Não contém prompts, histórico de conversas, modelo de IA, senhas, caminhos de pastas pessoais ou arquivos ANCRONOS/CHAOS WORLD.

## Custo de serviços: R$0

A configuração usa apenas repositório público e runner Linux padrão `ubuntu-24.04`, com limite de cinco minutos por execução. Ela bloqueia a execução caso o repositório se torne privado. Não usa runners ampliados, APIs de IA, cache, Git LFS, armazenamento de artefatos ou hospedagem paga. Os pequenos resultados são commits no próprio repositório.

- [GitHub: gratuidade de runners padrão em repositórios públicos](https://docs.github.com/en/actions/concepts/billing-and-usage)
- [GitHub: cobranças e armazenamento](https://docs.github.com/en/billing/concepts/product-billing/github-actions)
- [GitHub: limitações de horários agendados](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)
- [USGS: catálogo e regras de consulta](https://earthquake.usgs.gov/fdsnws/event/1/)

## Conferir os arquivos manualmente

```text
python3 apurar.py --verificar
python3 -m unittest -v teste_nuvem.py
```

Para obter o resultado real, somente dentro da janela permitida:

```text
python3 apurar.py
```
