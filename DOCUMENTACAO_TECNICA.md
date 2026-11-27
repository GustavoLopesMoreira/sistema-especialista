# DermaTech — Documentação técnica

## 1. Contexto do negócio

O DermaTech é um protótipo acadêmico de aplicação para uma clínica de estética. Seu objetivo é organizar a triagem inicial do cliente e sugerir um eixo de atendimento e um profissional de referência. Não realiza diagnóstico, não prescreve procedimentos e não substitui avaliação presencial.

## 2. Representação do conhecimento

### Fatos informados
- `queixa`: queixa principal selecionada no catálogo.
- `gravidade`: leve, moderada ou intensa.
- `duracao`: período relatado pelo cliente.
- `sensibilidade`: resposta sobre sensibilidade da pele.
- `alergia` e `alergia_detalhe`: indicação e descrição de alergia conhecida.
- `avaliacao_anterior`: se já houve avaliação profissional para a queixa.

### Fatos derivados
- `area` e `profissional`: eixo de atendimento e profissional de referência.
- `prioridade` e `marcador`: informações auxiliares para organizar o encaminhamento.
- `tipo_avaliacao`: classificação do encaminhamento inicial.
- `triagem_completa` e `encaminhamento_definido`: marcadores de conclusão.
- `alergia_detalhe_registrada`: confirma que a descrição da alergia foi incluída.

## 3. Base de conhecimento — 32 regras

A base possui **32 regras de produção (R01–R32)**, declaradas em `engine.py`.

| Faixa | Finalidade |
|---|---|
| R01–R11 | Relacionar a queixa principal com a área e o profissional de referência |
| R12–R20 | Considerar gravidade, sensibilidade, alergias, duração e avaliação anterior |
| R21–R25 | Definir o tipo de avaliação conforme a área indicada |
| R26–R28 | Registrar coleta de dados, eixo de atendimento e descrição de alergia |
| R29–R32 | Combinar dois ou mais fatos para enriquecer a sinalização do encaminhamento |

### Exemplos de regras combinadas

- **R29 — Queixa intensa e persistente:** combina gravidade intensa e duração superior a seis meses para registrar uma sinalização de atenção prioritária à avaliação presencial.
- **R30 — Queixa moderada e persistente com sensibilidade:** combina gravidade moderada, duração superior a seis meses e sensibilidade relatada.
- **R31 — Alergia relatada junto com sensibilidade:** combina alergia descrita e sensibilidade relatada.
- **R32 — Queixa intensa com alergia informada:** combina gravidade intensa e descrição de alergia.

Essas regras organizam informações para a avaliação humana e não representam diagnóstico ou decisão clínica.

Cada item da lista `RULES` contém identificador, descrição, condição, conclusão e fator heurístico.

## 4. Motor de inferência

A função `executar_inferencia(fatos_iniciais)`, localizada em `engine.py`, implementa **encadeamento para frente (Forward Chaining)**.

1. Copia os fatos informados pelo usuário.
2. Percorre as regras que ainda não foram acionadas.
3. Avalia as condições de cada regra com base nos fatos disponíveis.
4. Quando uma condição é satisfeita, registra a regra e adiciona ou atualiza os fatos derivados.
5. Repete o ciclo até não encontrar uma nova regra aplicável.

O motor retorna os fatos finais, regras acionadas, condição avaliada, fatos derivados, fator heurístico, número de ciclos e conclusão.

## 5. Explicação do raciocínio

A interface apresenta:
- fatos informados como ponto de partida;
- cada regra acionada em ordem;
- condição avaliada;
- fatos adicionados ou atualizados;
- ciclo em que a regra foi aplicada;
- ponto de parada, quando nenhuma regra nova é encontrada;
- conclusão final.

O índice heurístico acumulado é calculado pelo produto dos fatores das regras acionadas. É um indicador demonstrativo e **não representa probabilidade clínica**.

## 6. Testes automatizados

Os testes ficam em `tests/test_engine.py` e usam `pytest`. A suíte atual contém 12 testes que verificam:
- quantidade mínima e identificadores únicos das regras;
- encaminhamento esperado para as onze queixas cadastradas;
- ordem e conteúdo do rastreio do Forward Chaining;
- preservação dos fatos de entrada;
- acionamento individual de R29, R30, R31 e R32;
- não acionamento de regras combinadas quando faltam condições;
- ausência de conclusão para queixa fora do catálogo;
- tratamento de fatos ausentes;
- presença de condições e fatores heurísticos nas regras acionadas.

Para executar os testes:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest
```

## 7. Tratamento de exceções

A aplicação:
- exige a descrição da alergia quando a resposta for “Sim”;
- valida nome, e-mail e telefone antes de registrar uma solicitação;
- verifica se a data e o horário continuam disponíveis;
- impede solicitações em datas passadas, domingos, 1º de janeiro, 25 de dezembro e datas sem horários livres para o profissional;
- informa explicitamente quando não é possível chegar a uma conclusão com os fatos fornecidos.

## 8. Agendamento

O formulário utiliza o seletor de data nativo do Streamlit. Os horários demonstrativos vão de 09h a 19h, com pausa no almoço. A disponibilidade é verificada por profissional e conferida novamente no envio da solicitação.

## 9. Execução da aplicação

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## 10. Limitações

Os registros ficam na sessão ativa do Streamlit, sem persistência em banco de dados. Datas de fechamento, equipe, horários e avaliações são dados demonstrativos do cenário acadêmico.
