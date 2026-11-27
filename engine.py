
RULES = [
    ("R01","Queixa relacionada a acne","queixa == 'Acne e oleosidade'",{"area":"Biomedicina estética","profissional":"Helena Martins"},.92),
    ("R02","Queixa relacionada a manchas ou melasma","queixa == 'Manchas e melasma'",{"area":"Dermatologia","profissional":"Caio Nogueira"},.94),
    ("R03","Queixa relacionada a linhas ou rugas","queixa == 'Linhas e rugas'",{"area":"Biomedicina estética","profissional":"Luiza Fernandes"},.90),
    ("R04","Queixa relacionada à firmeza ou flacidez","queixa == 'Firmeza e flacidez da pele'",{"area":"Fisioterapia dermatofuncional","profissional":"Mariana Costa"},.91),
    ("R05","Queixa relacionada a ressecamento","queixa == 'Ressecamento da pele'",{"area":"Estética e cosmetologia","profissional":"Beatriz Almeida"},.88),
    ("R06","Queixa relacionada a sensibilidade ou vermelhidão","queixa == 'Sensibilidade e vermelhidão'",{"area":"Dermatologia","profissional":"Caio Nogueira"},.93),
    ("R07","Queixa relacionada a poros e textura","queixa == 'Poros dilatados e textura irregular'",{"area":"Biomedicina estética","profissional":"Helena Martins"},.87),
    ("R08","Queixa relacionada a olheiras","queixa == 'Olheiras'",{"area":"Biomedicina estética","profissional":"Luiza Fernandes"},.87),
    ("R09","Queixa relacionada a cicatrizes de acne","queixa == 'Cicatrizes de acne'",{"area":"Fisioterapia dermatofuncional","profissional":"Rafael Mendes"},.90),
    ("R10","Busca por cuidados preventivos","queixa == 'Cuidados preventivos'",{"area":"Estética e cosmetologia","profissional":"Beatriz Almeida"},.86),
    ("R11","Queixa não contemplada no catálogo","queixa == 'Outras queixas'",{"area":"Avaliação geral","profissional":"Equipe DermaTech"},.80),
    ("R12","Queixa com gravidade leve","gravidade == 'Leve'",{"prioridade":"Rotina"},.90),
    ("R13","Queixa com gravidade moderada","gravidade == 'Moderada'",{"prioridade":"Atenção"},.90),
    ("R14","Queixa com gravidade intensa","gravidade == 'Intensa'",{"prioridade":"Atenção prioritária"},.92),
    ("R15","Relato de pele sensível","sensibilidade == 'Sim'",{"marcador":"Relatar sensibilidade na avaliação"},.95),
    ("R16","Relato de alergia","alergia == 'Sim'",{"marcador":"Informar alergias ao profissional"},.98),
    ("R17","Queixa persistente","duracao == 'Mais de 6 meses'",{"marcador":"Relatar persistência da queixa"},.88),
    ("R18","Queixa recente","duracao == 'Até 3 meses'",{"marcador":"Registrar início recente"},.86),
    ("R19","Já realizou avaliação profissional","avaliacao_anterior == 'Sim'",{"marcador":"Levar histórico da avaliação anterior"},.90),
    ("R20","Ainda não realizou avaliação profissional","avaliacao_anterior == 'Não'",{"marcador":"Priorizar avaliação inicial"},.90),
    ("R21","Encaminhamento dermatológico","area == 'Dermatologia'",{"tipo_avaliacao":"Avaliação dermatológica inicial"},.94),
    ("R22","Encaminhamento de biomedicina estética","area == 'Biomedicina estética'",{"tipo_avaliacao":"Avaliação inicial em biomedicina estética"},.90),
    ("R23","Encaminhamento de fisioterapia dermatofuncional","area == 'Fisioterapia dermatofuncional'",{"tipo_avaliacao":"Avaliação em fisioterapia dermatofuncional"},.90),
    ("R24","Encaminhamento de estética e cosmetologia","area == 'Estética e cosmetologia'",{"tipo_avaliacao":"Avaliação inicial em estética e cosmetologia"},.88),
    ("R25","Encaminhamento geral","area == 'Avaliação geral'",{"tipo_avaliacao":"Avaliação geral para entender a necessidade"},.82),
    ("R26","Dados de triagem coletados","queixa != '' and gravidade != ''",{"triagem_completa":True},.99),
    ("R27","Eixo de atendimento identificado","'area' in fatos",{"encaminhamento_definido":True},.99),
    ("R28","Descrição de alergia informada","alergia == 'Sim' and alergia_detalhe != ''",{"alergia_detalhe_registrada":True},.99),

    ("R29","Queixa intensa e persistente","gravidade == 'Intensa' and duracao == 'Mais de 6 meses'",{"prioridade":"Atenção prioritária","marcador":"Destacar combinação de intensidade e persistência para avaliação presencial"},.98),
    ("R30","Queixa moderada e persistente com sensibilidade","gravidade == 'Moderada' and duracao == 'Mais de 6 meses' and sensibilidade == 'Sim'",{"marcador":"Registrar persistência associada à sensibilidade para a avaliação"},.96),
    ("R31","Alergia relatada junto com sensibilidade","alergia == 'Sim' and alergia_detalhe != '' and sensibilidade == 'Sim'",{"marcador":"Informar ao profissional a alergia descrita e o relato de sensibilidade"},.98),
    ("R32","Queixa intensa com alergia informada","gravidade == 'Intensa' and alergia == 'Sim' and alergia_detalhe != ''",{"marcador":"Destacar a alergia informada durante a avaliação presencial"},.98),
]

def executar_inferencia(fatos_iniciais):
    """Aplica regras por encadeamento para frente e registra cada etapa.

    O motor parte dos fatos informados, percorre as regras ainda não aplicadas
    e adiciona/atualiza fatos derivados. O ciclo termina quando nenhuma regra
    nova é acionada.
    """
    fatos = dict(fatos_iniciais)
    aplicadas = set()
    explicacoes = []
    certeza = 1.0
    ciclo = 0

    while True:
        ciclo += 1
        houve_mudanca = False

        for rid, descricao, condicao, conclusao, cf in RULES:
            if rid in aplicadas:
                continue

            try:
                condicao_atendida = eval(
                    condicao,
                    {"__builtins__": {}},
                    {**fatos, "fatos": fatos},
                )
            except Exception:
                condicao_atendida = False

            if not condicao_atendida:
                continue

            # Registra quais fatos foram efetivamente criados ou atualizados.
            fatos_derivados = {
                chave: valor
                for chave, valor in conclusao.items()
                if fatos.get(chave) != valor
            }
            fatos_anteriores = {
                chave: fatos.get(chave)
                for chave in conclusao
                if chave in fatos
            }
            fatos.update(conclusao)
            aplicadas.add(rid)
            certeza *= cf
            explicacoes.append({
                "id": rid,
                "descricao": descricao,
                "condicao": condicao,
                "conclusao": conclusao,
                "fatos_anteriores": fatos_anteriores,
                "fatos_derivados": fatos_derivados,
                "cf": cf,
                "etapa": len(explicacoes) + 1,
                "ciclo": ciclo,
            })
            houve_mudanca = True

        if not houve_mudanca:
            break

    return {
        "fatos": fatos,
        "regras": explicacoes,
        "certeza": certeza,
        "conclusao": fatos.get("tipo_avaliacao"),
        "ciclos": ciclo,
        "total_regras": len(RULES),
    }
