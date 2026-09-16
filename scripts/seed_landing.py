"""Move o acervo legado para data/00_landing/<id>/seed/ e apaga pastas *_files.

Idempotente: se a origem já não existe, segue.
"""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
LANDING = DATA / "00_landing"

# (source_id, fragment único no nome legado, nome canônico)
PDFS: list[tuple[str, str, str]] = [
    (
        "anuario_cerveja_ref2021_pub2022",
        "anuario-da-cerveja-2021",
        "anuario_cerveja_ref2021_pub2022.pdf",
    ),
    (
        "anuario_cerveja_ref2022_pub2023",
        "anuario-da-cerveja-2022",
        "anuario_cerveja_ref2022_pub2023.pdf",
    ),
    (
        "anuario_cerveja_ref2023_pub2024",
        "anuario-da-cerveja-2023",
        "anuario_cerveja_ref2023_pub2024.pdf",
    ),
    (
        "anuario_cerveja_ref2024_pub2025",
        "anuario-da-cerveja-2024",
        "anuario_cerveja_ref2024_pub2025.pdf",
    ),
    (
        "anuario_cerveja_ref2025_pub2026",
        "anuario-da-cerveja-2025",
        "anuario_cerveja_ref2025_pub2026.pdf",
    ),
    (
        "cisa_panorama_alcool_saude_2023",
        "Panorama_Alcool_Saude_CISA2023",
        "cisa_panorama_alcool_saude_2023.pdf",
    ),
    (
        "araujo_tcc_cerveja_ufrgs_2025",
        "tcc_sobre_consumo",
        "araujo_tcc_cerveja_habitos_consumo_ufrgs_2025.pdf",
    ),
    ("bcb_ee119_apostas_2024", "EE119_Analise_tecnica", "bcb_ee119_apostas_online_2024.pdf"),
    ("fundaj_nt39_pce_2024", "NotaTcnica39", "fundaj_nt39_pce_apostas_bolsa_familia.pdf"),
    (
        "ieps_dossie_bets_saude",
        "dossie-_bets-saude",
        "ieps_dossie_bets_saude_brasileiros_em_jogo.pdf",
    ),
    (
        "strategy_impacto_apostas_consumo_2024",
        "impacto_apostas_esportivas_consumo",
        "public_strategy_impacto_apostas_consumo_2024.pdf",
    ),
    (
        "amaro_bets_publicidade_intercom_2024",
        "bet 2.pdf",
        "amaro_apostas_esportivas_publicidade_intercom_2024.pdf",
    ),
    (
        "elkhatib_bets_universitarios_2024",
        "bet.pdf",
        "elkhatib_diversao_ou_armadilha_bets_universitarios_2024.pdf",
    ),
    (
        "lca_ibjr_anjl_panorama_apostas_2025",
        "LCA_Cruz_IBJR_ANJL_Panorama-2025-Setor",
        "lca_ibjr_anjl_panorama_quota_fixa_nov2025.pdf",
    ),
]

HTMLS: list[tuple[str, str, str]] = [
    (
        "web_senado_mercado_global_bets_2026",
        "quinto maior mercado",
        "radio_senado_quinto_mercado_global_bets_2026.html",
    ),
    (
        "web_valor_klavi_apostadores_2026",
        "apostadores dobra",
        "valor_investe_apostadores_dobram_klavi_2026.html",
    ),
    ("web_klavi_placar_bets", "Placar da Copa", "klavi_placar_das_bets.html"),
    (
        "web_g1_propaganda_bets_2025",
        "Propaganda de dinheiro",
        "g1_propaganda_dinheiro_facil_bets_2025.html",
    ),
    ("web_catalisi_consumo_2022", "16 bilh", "catalisi_consumo_cerveja_2022.html"),
    ("web_istoe_sem_alcool", "Alemanha", "istoe_cerveja_sem_alcool.html"),
    ("web_exame_zero_885mi", "885", "exame_cerveja_zero_885mi.html"),
    ("web_g1_consumo_cerveja_2024", "voltar a crescer", "g1_consumo_cerveja_2024.html"),
    (
        "web_central_varejo_sem_alcool",
        "Central do Varejo",
        "central_varejo_cervejas_sem_alcool.html",
    ),
    ("web_cnn_ifood_copa", "iFood", "cnn_ifood_estreia_selecao_bebidas.html"),
    ("web_catalisi_vendas_2021", "14,3", "catalisi_vendas_cerveja_2021.html"),
]


def _norm(name: str) -> str:
    return name.casefold()


def _already_canonical(path: Path) -> bool:
    try:
        rel = path.relative_to(LANDING)
    except ValueError:
        return False
    return len(rel.parts) >= 3 and rel.parts[1] == "seed"


def _find(fragment: str, suffix: str) -> Path | None:
    needle = _norm(fragment)
    matches = [
        path
        for path in DATA.rglob(f"*{suffix}")
        if "_files" not in path.parts
        and needle in _norm(path.name)
        and not _already_canonical(path)
    ]
    if not matches:
        return None
    if len(matches) > 1:
        # bet.pdf vs bet 2.pdf: prefer exact name match when fragment is a full filename
        exact = [path for path in matches if _norm(path.name) == needle]
        if len(exact) == 1:
            return exact[0]
        raise SystemExit(f"fragmento ambíguo '{fragment}': {matches}")
    return matches[0]


def _move(source_id: str, src: Path, filename: str) -> None:
    dest_dir = LANDING / source_id / "seed"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / filename
    if dest.exists() and src.resolve() != dest.resolve():
        src.unlink()
        print(f"skip (já no lake), remove origem: {src}")
        return
    shutil.move(str(src), str(dest))
    print(f"move {src.name} -> {dest.relative_to(ROOT)}")


def main() -> None:
    LANDING.mkdir(parents=True, exist_ok=True)

    for source_id, fragment, filename in PDFS:
        src = _find(fragment, ".pdf")
        if src is None:
            dest = LANDING / source_id / "seed" / filename
            print(f"ok  {dest.relative_to(ROOT)}" if dest.exists() else f"MISS pdf {fragment}")
            continue
        _move(source_id, src, filename)

    for source_id, fragment, filename in HTMLS:
        src = _find(fragment, ".html")
        if src is None:
            dest = LANDING / source_id / "seed" / filename
            print(f"ok  {dest.relative_to(ROOT)}" if dest.exists() else f"MISS html {fragment}")
            continue
        _move(source_id, src, filename)

    for folder in list(DATA.rglob("*")):
        if folder.is_dir() and folder.name.endswith("_files"):
            shutil.rmtree(folder)
            print(f"rmtree {folder.relative_to(ROOT)}")

    for leftover in (DATA / "bet", DATA / "cerveja"):
        if leftover.exists():
            shutil.rmtree(leftover)
            print(f"rmtree {leftover.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
