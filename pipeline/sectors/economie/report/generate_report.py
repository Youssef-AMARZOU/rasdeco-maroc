"""
generate_report.py — Generation automatisee de la synthese conjoncturelle.

Contraintes strictes :
  1. N'utilise QUE les chiffres du JSON d'entree (zero hallucination numerique).
  2. Signale explicitement les donnees manquantes ou de fiabilite faible.
  3. Longueur cible : 250-350 mots.
  4. Aucune causalite affirmee sans preuve dans les donnees.

Usage :
    python generate_report.py kpis_example.json -o synthese.md
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Modele
# ---------------------------------------------------------------------------
@dataclass
class Kpi:
    code: str
    label: str
    unit: str
    quality: str = "standard"
    interpretation: str = ""
    value: float | None = None
    delta: float | None = None
    delta_unit: str = ""


# ---------------------------------------------------------------------------
# Chargement
# ---------------------------------------------------------------------------
def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def parse_kpis(data: dict) -> tuple[str, list[Kpi]]:
    periode = data.get("meta", data).get("periode", "periode inconnue")
    raw_list = data.get("indicateurs", [])
    kpis = []
    for item in raw_list:
        kpis.append(Kpi(
            code=item.get("code", "?"),
            label=item.get("label", "?"),
            value=item.get("value"),
            unit=item.get("unit", ""),
            delta=item.get("delta"),
            delta_unit=item.get("delta_unit", ""),
            quality=item.get("quality", "standard"),
            interpretation=item.get("interpretation", ""),
        ))
    return periode, kpis


# ---------------------------------------------------------------------------
# Formatage (decimale francaise)
# ---------------------------------------------------------------------------
def _dec(n: float | None) -> str:
    """Formate un float en notation francaise (virgule, pas de zero inutile)."""
    if n is None:
        return "N/D"
    s = f"{n:.2f}".replace(".", ",")
    return s


def _fmt_val(kpi: Kpi) -> str:
    if kpi.value is None:
        return "**donnee manquante**"
    return f"**{_dec(kpi.value)} {kpi.unit}**"


def _fmt_delta(kpi: Kpi) -> str:
    if kpi.delta is None:
        return "variation non disponible"
    sign = "+" if kpi.delta >= 0 else "\u2212"
    abs_d = abs(kpi.delta)
    return f"{sign}{_dec(abs_d)} {kpi.delta_unit} vs periode precedente"


# ---------------------------------------------------------------------------
# Phrases d'interpretation par defaut
# ---------------------------------------------------------------------------
def _fallback_interp(kpi: Kpi) -> str:
    """Interpretation neutre quand aucune n'est fournie dans le JSON."""
    if kpi.value is None:
        return "Aucune valeur disponible pour cet indicateur."
    return ""


# ---------------------------------------------------------------------------
# Section indicateur
# ---------------------------------------------------------------------------
def _section(kpi: Kpi) -> str:
    pieces = [f"**{kpi.label} : {_fmt_val(kpi)}** ({_fmt_delta(kpi)})."]

    if kpi.value is None:
        pieces.append("Donnee manquante pour cette periode : indicateur non interpretable.")
    elif kpi.quality == "faible":
        pieces.append("Fiabilite faible signalee par le controle qualite : a lire avec prudence.")
    elif kpi.quality == "manquante":
        pieces.append("Indicateur non collecte pour cette fenetre.")

    texte_interp = kpi.interpretation or _fallback_interp(kpi)
    if texte_interp:
        pieces.append(texte_interp)

    return " ".join(pieces)


# ---------------------------------------------------------------------------
# Synthese generale (builder automatique)
# ---------------------------------------------------------------------------
def _build_synthese(kpis: list[Kpi]) -> str:
    """Construit un paragraphe de synthese a partir des seuls chiffres disponibles."""
    index = {k.code: k for k in kpis}
    phrases = []

    pib = index.get("pib")
    if pib and pib.value is not None:
        phrases.append(f"La croissance du PIB s'etablit a {_dec(pib.value)} %")

    inflation = index.get("inflation")
    if inflation and inflation.value is not None:
        phrases.append(f"l'inflation a {_dec(inflation.value)} %")

    taux = index.get("taux_directeur")
    if taux and taux.value is not None:
        phrases.append(f"le taux directeur BAM a {_dec(taux.value)} %")

    # Joindre les 2-3 premiers elements
    if len(phrases) >= 2:
        debut = ", ".join(phrases[:-1]) + " et " + phrases[-1]
    elif phrases:
        debut = phrases[0]
    else:
        debut = ""

    # Ajouter des complements
    complements = []
    dette = index.get("dette_pib")
    if dette and dette.value is not None:
        complements.append(f"La dette publique atteint {_dec(dette.value)} % du PIB")

    deficit = index.get("deficit")
    if deficit and deficit.value is not None:
        complements.append(f"le deficit budgetaire est reduit a {_dec(deficit.value)} % du PIB")

    reserves = index.get("reserves_change")
    if reserves and reserves.value is not None:
        complements.append(f"les reserves de change a {_dec(reserves.value)} mois d'importation")

    texte_complements = ". ".join(complements)

    if debut and texte_complements:
        return f"{debut}, {texte_complements.lower()}."
    elif debut:
        return f"{debut}."
    elif texte_complements:
        return f"{texte_complements}."
    return "Aucun indicateur disponible pour cette periode."


# ---------------------------------------------------------------------------
# Points de vigilance
# ---------------------------------------------------------------------------
def _vigilance(kpis: list[Kpi]) -> list[str]:
    regles = [
        ("reserves_change", lambda k: k.value is not None and k.value < 3.0,
         lambda k: f"Reserves de change a {_dec(k.value)} mois, sous le seuil de 3 mois d'importation : marge de man\u0153uvre reduite en cas de choc externe."),
        ("inflation", lambda k: k.value is not None and k.value < 1.0,
         lambda k: f"Inflation a {_dec(k.value)} % : un niveau bas peut refleter une faiblesse de la demande interieure."),
        ("dette_pib", lambda k: k.value is not None and k.delta is not None and k.delta > 0,
         lambda k: f"Dette publique/PIB a {_dec(k.value)} %, en progression continue : trajectoire a surveiller."),
    ]
    index = {k.code: k for k in kpis}
    points = []
    for code, condition, message in regles:
        k = index.get(code)
        if k and condition(k):
            points.append(message(k))

    # Ajouter les series degradees
    faibles = [k for k in kpis if k.quality in ("faible", "manquante")]
    if faibles:
        noms = ", ".join(k.label for k in faibles)
        points.append(f"Qualite de serie degradee sur : {noms}.")

    return points[:3]


# ---------------------------------------------------------------------------
# Compteur de mots
# ---------------------------------------------------------------------------
def _compte_mots(texte: str) -> int:
    return len(texte.split())


# ---------------------------------------------------------------------------
# Generateur principal
# ---------------------------------------------------------------------------
def generer(
    periode: str,
    kpis: list[Kpi],
    synthese_generale: str | None = None,
) -> str:
    """
    Assemble le rapport Markdown.

    Parametres
    ----------
    periode : etiquette de periode (ex. "2025-2026")
    kpis : liste des indicateurs
    synthese_generale : si None, generee automatiquement depuis les KPIs
    """
    if synthese_generale is None:
        synthese_generale = _build_synthese(kpis)

    lignes = [
        "## Synthese conjoncturelle - Module ECONOMIE",
        f"**Periode : {periode}**",
        "",
        "### Synthese generale",
        synthese_generale,
        "",
        "### Indicateurs",
        "",
    ]

    for kpi in kpis:
        lignes.append(_section(kpi))
        lignes.append("")

    lignes.append("### Points de vigilance")
    for p in _vigilance(kpis):
        lignes.append(f"- {p}")

    # Si aucun point declenche, message par defaut
    if not _vigilance(kpis):
        lignes.append("- Aucun seuil de vigilance declenche pour cette periode.")

    texte = "\n".join(lignes).strip()
    nb = _compte_mots(texte)

    # Avertissement si hors cible
    if not 250 <= nb <= 350:
        texte += f"\n\n<!-- AVERTISSEMENT : {nb} mots, hors cible 250-350 -->"

    return texte


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    import argparse
    parser = argparse.ArgumentParser(description="Genere la synthese ECONOMIE.")
    parser.add_argument("input", help="Fichier JSON des KPIs")
    parser.add_argument("-o", "--output", default="synthese.md",
                        help="Fichier de sortie (defaut: synthese.md)")
    parser.add_argument("-s", "--synthese", default=None,
                        help="Texte de synthese generale (optionnel)")
    args = parser.parse_args()

    data = load_json(args.input)
    periode, kpis = parse_kpis(data)

    rapport = generer(
        periode=periode,
        kpis=kpis,
        synthese_generale=args.synthese,
    )

    Path(args.output).write_text(rapport, encoding="utf-8")
    nb = _compte_mots(rapport)
    print(f"Rapport ecrit dans {args.output} ({nb} mots)")
    if not 250 <= nb <= 350:
        print(f"  AVERTISSEMENT : {nb} mots, cible 250-350")


if __name__ == "__main__":
    main()
