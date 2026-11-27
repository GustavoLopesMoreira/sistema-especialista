from engine import RULES, executar_inferencia


BASE_FACTS = {
    "queixa": "Acne e oleosidade",
    "gravidade": "Moderada",
    "duracao": "Até 3 meses",
    "sensibilidade": "Não",
    "alergia": "Não",
    "alergia_detalhe": "",
    "avaliacao_anterior": "Não",
}


def run_case(**overrides):
    facts = {**BASE_FACTS, **overrides}
    return executar_inferencia(facts)


def test_base_has_at_least_twenty_rules_and_unique_ids():
    ids = [rule[0] for rule in RULES]
    assert len(RULES) == 32
    assert len(RULES) >= 20
    assert len(ids) == len(set(ids))
    assert ids[0] == "R01"
    assert ids[-1] == "R32"


def test_all_complaints_map_to_expected_reference_professional():
    expected = {
        "Acne e oleosidade": "Helena Martins",
        "Manchas e melasma": "Caio Nogueira",
        "Linhas e rugas": "Luiza Fernandes",
        "Firmeza e flacidez da pele": "Mariana Costa",
        "Ressecamento da pele": "Beatriz Almeida",
        "Sensibilidade e vermelhidão": "Caio Nogueira",
        "Poros dilatados e textura irregular": "Helena Martins",
        "Olheiras": "Luiza Fernandes",
        "Cicatrizes de acne": "Rafael Mendes",
        "Cuidados preventivos": "Beatriz Almeida",
        "Outras queixas": "Equipe DermaTech",
    }

    for complaint, professional in expected.items():
        result = run_case(queixa=complaint)
        assert result["fatos"]["profissional"] == professional
        assert result["conclusao"]


def test_forward_chaining_creates_explanation_trace():
    result = run_case()
    rules = [entry["id"] for entry in result["regras"]]

    assert "R01" in rules
    assert "R22" in rules
    assert "R27" in rules
    assert result["regras"][0]["etapa"] == 1
    assert [entry["etapa"] for entry in result["regras"]] == list(
        range(1, len(result["regras"]) + 1)
    )
    assert all("condicao" in entry for entry in result["regras"])
    assert all("fatos_derivados" in entry for entry in result["regras"])
    assert result["ciclos"] >= 1


def test_engine_does_not_mutate_initial_facts():
    initial = dict(BASE_FACTS)
    before = dict(initial)

    executar_inferencia(initial)

    assert initial == before


def test_intense_and_persistent_complaint_activates_r29():
    result = run_case(gravidade="Intensa", duracao="Mais de 6 meses")
    ids = {entry["id"] for entry in result["regras"]}

    assert "R29" in ids
    assert result["fatos"]["prioridade"] == "Atenção prioritária"
    assert "intensidade e persistência" in result["fatos"]["marcador"]


def test_moderate_persistent_and_sensitive_complaint_activates_r30():
    result = run_case(
        gravidade="Moderada",
        duracao="Mais de 6 meses",
        sensibilidade="Sim",
    )
    ids = {entry["id"] for entry in result["regras"]}

    assert "R30" in ids
    assert "persistência associada à sensibilidade" in result["fatos"]["marcador"]


def test_allergy_and_sensitivity_combination_activates_r31():
    result = run_case(
        alergia="Sim",
        alergia_detalhe="Fragrância",
        sensibilidade="Sim",
    )
    ids = {entry["id"] for entry in result["regras"]}

    assert "R16" in ids
    assert "R28" in ids
    assert "R31" in ids
    assert result["fatos"]["alergia_detalhe_registrada"] is True


def test_intense_complaint_with_described_allergy_activates_r32():
    result = run_case(
        gravidade="Intensa",
        alergia="Sim",
        alergia_detalhe="Determinado cosmético",
    )
    ids = {entry["id"] for entry in result["regras"]}

    assert "R32" in ids
    assert "alergia informada" in result["fatos"]["marcador"]


def test_combination_rules_do_not_fire_when_conditions_are_missing():
    result = run_case(
        gravidade="Moderada",
        duracao="Mais de 6 meses",
        sensibilidade="Não",
        alergia="Não",
        alergia_detalhe="",
    )
    ids = {entry["id"] for entry in result["regras"]}

    assert "R30" not in ids
    assert "R31" not in ids
    assert "R32" not in ids


def test_unknown_complaint_has_no_conclusion():
    result = run_case(queixa="Queixa fora do catálogo")

    assert result["conclusao"] is None
    assert "area" not in result["fatos"]
    assert "profissional" not in result["fatos"]


def test_missing_or_incomplete_facts_do_not_crash_engine():
    result = executar_inferencia({})

    assert result["conclusao"] is None
    assert isinstance(result["regras"], list)
    assert result["total_regras"] == len(RULES)


def test_every_fired_rule_has_condition_and_heuristic_factor():
    result = run_case()

    assert result["regras"]
    for entry in result["regras"]:
        assert entry["id"].startswith("R")
        assert entry["condicao"]
        assert 0 < entry["cf"] <= 1
        assert isinstance(entry["conclusao"], dict)
