from betscerveja.registry import load_registry


def test_sources_yml_valida() -> None:
    registry = load_registry()
    assert len(registry.sources) >= 20
    ids = [source.id for source in registry.sources]
    assert len(ids) == len(set(ids))


def test_anuarios_separam_referencia_de_vintage() -> None:
    registry = load_registry()
    pub2025 = registry.get("anuario_cerveja_ref2024_pub2025")
    pub2026 = registry.get("anuario_cerveja_ref2025_pub2026")
    assert pub2025.ano_referencia == 2024
    assert pub2025.vintage_publicacao == 2025
    assert pub2026.ano_referencia == 2025
    assert pub2026.vintage_publicacao == 2026


def test_cisa_tem_conflito_de_interesse() -> None:
    source = load_registry().get("cisa_panorama_alcool_saude_2023")
    assert source.conflito_de_interesse
    assert source.tier_confiabilidade == "C"


def test_spa_panorama_esta_pendente() -> None:
    source = load_registry().get("spa_panorama_apostas_2025")
    assert source.status_acervo == "pendente"
    assert source.e_oficial is True


def test_lca_ibjr_nao_e_spa() -> None:
    source = load_registry().get("lca_ibjr_anjl_panorama_apostas_2025")
    assert source.status_acervo == "no_lake"
    assert source.e_oficial is False
    assert source.tier_confiabilidade == "C"
    assert source.conflito_de_interesse
    assert source.landing_filename == "lca_ibjr_anjl_panorama_quota_fixa_nov2025.pdf"
