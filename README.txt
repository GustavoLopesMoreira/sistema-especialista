DERMATECH — SISTEMA ESPECIALISTA EM PYTHON + STREAMLIT

EXECUÇÃO DA APLICAÇÃO
1. Instale Python 3.10 ou superior.
2. Abra o terminal dentro desta pasta.
3. Instale as dependências: python -m pip install -r requirements.txt
4. Inicie: python -m streamlit run app.py

EXECUÇÃO DOS TESTES AUTOMATIZADOS
1. Instale as dependências de desenvolvimento: python -m pip install -r requirements-dev.txt
2. Execute: python -m pytest
O conjunto atual contém 12 testes automatizados sobre a base de regras, os encaminhamentos,
as regras combinadas, o rastreio de inferência e os casos sem conclusão.

ESTRUTURA DO PROJETO
- app.py: interface Streamlit, triagem, agendamento, recepção e apresentação do raciocínio.
- engine.py: base de conhecimento com 32 regras e motor de inferência Forward Chaining.
- tests/test_engine.py: testes automatizados do motor de inferência.
- DOCUMENTACAO_TECNICA.md: documentação da representação do conhecimento, regras, inferência e testes.
- assets/: retratos da equipe e imagens da recepção e do espaço de conversa.

SISTEMA ESPECIALISTA
- Abordagem: Python com motor de regras próprio.
- Inferência: encadeamento para frente (Forward Chaining).
- Base de conhecimento: 32 regras de produção (R01 a R32).
- Regras combinadas: R29 a R32 consideram múltiplos fatos simultaneamente.
- Explicação: a tela de resultado apresenta fatos iniciais, cada regra acionada, condição avaliada,
  fatos derivados e ponto de parada do encadeamento.
- Incerteza: fatores heurísticos associados às regras; o índice acumulado não representa probabilidade clínica.
- Exceções: entradas inválidas e ausência de conclusão são informadas ao usuário.

NOTA SOBRE O PROTÓTIPO
O DermaTech é um protótipo acadêmico de triagem inicial para uma clínica de estética.
Não realiza diagnóstico nem prescreve procedimentos. Nomes, fotografias, avaliações e horários
pertencem ao cenário demonstrativo. Os agendamentos ficam na sessão do Streamlit, sem persistência
em banco de dados.

Ajuste visual: aviso de alergia obrigatória com texto verde-escuro sobre fundo amarelo-claro para garantir contraste.
