"""
extractor.py — Extraction deux flux (texte + tableaux) depuis un PDF.

Utilise pdfplumber pour :
  - Flux texte : paragraphes avec numero de page, style (gras, taille police)
  - Flux tableaux : tableaux bruts avec en-tetes et numero de page

Ne jamais aplatir un tableau dans le flux textuel.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator

from pdfplumber.page import Page


@dataclass
class TextElement:
    """Element textuel preserve (paragraphe ou titre)."""
    page_num: int
    text: str
    font_size: float = 12.0
    is_bold: bool = False
    bbox: tuple[float, float, float, float] | None = None
    type: str = "paragraph"  # title | subtitle | paragraph


@dataclass
class TableElement:
    """Tableau preserve en format brut + Markdown."""
    page_num: int
    rows: list[list[str | None]]
    headers: list[str]
    title: str = ""
    footnote: str = ""
    bbox: tuple[float, float, float, float] | None = None


@dataclass
class ExtractionResult:
    """Resultat complet de l'extraction d'un PDF."""
    source_path: str = ""
    titre_document: str = ""
    date_publication: str = ""
    periode_couverte: str = ""
    organisme: str = ""
    text_elements: list[TextElement] = field(default_factory=list)
    table_elements: list[TableElement] = field(default_factory=list)
    total_pages: int = 0


# ---------------------------------------------------------------------------
# Heuristiques de detection
# ---------------------------------------------------------------------------
_ORGANISMES = {
    r"bank\s*al[-\s]*maghrib": "BAM",
    r"bam": "BAM",
    r"haut[-\s]*commissariat": "HCP",
    r"hcp": "HCP",
    r"ministere\s*de\s*l['e]\s*economie": "MEF",
    r"office\s*des\s*changes": "OC",
    r"haut\s*commissariat\s*au\s*plan": "HCP",
}

_YEAR_PATTERNS = [
    r"(20[0-9]{2})\s*[-–]\s*(20[0-9]{2})",  # 2019-2020 ou 2019-20
    r"(20[0-9]{2})",
]

_FOOTNOTE_PATTERNS = [
    r"^(\d+)\s+",
    r"Source\s*:",
    r"\(1\)",
]


def _detect_organisme(texte: str) -> str:
    for pattern, org in _ORGANISMES.items():
        if re.search(pattern, texte, re.IGNORECASE):
            return org
    return ""


def _detect_periode(texte: str) -> str:
    for pat in _YEAR_PATTERNS:
        m = re.search(pat, texte)
        if m:
            return m.group(0)
    return ""


def _detect_titre(texte: str) -> str:
    lignes = [l.strip() for l in texte.split("\n") if l.strip()]
    for l in lignes[:10]:
        if re.search(r"rapport\s*(annuel|trimestriel|semestriel|annuel)", l, re.IGNORECASE):
            return l.strip()[:80]
    for l in lignes[:3]:
        if len(l) > 10:
            return l.strip()[:80]
    return "document sans titre"


def _detect_date_publication(texte: str) -> str:
    pats = [
        r"(\d{2}/\d{2}/20[0-9]{2})",
        r"(\d{2}-\d{2}-20[0-9]{2})",
        r"(20[0-9]{2})",
    ]
    for pat in pats:
        m = re.search(pat, texte[:500])
        if m:
            return m.group(1)
    return ""


# ---------------------------------------------------------------------------
# Extraction principale
# ---------------------------------------------------------------------------
def extract_pdf(path: str | Path) -> ExtractionResult:
    """
    Extrait un PDF en deux flux preserves : texte et tableaux.

    Parametres
    ----------
    path : chemin du fichier PDF

    Retourne
    --------
    ExtractionResult avec text_elements et table_elements separes.
    """
    import pdfplumber

    path = Path(path)
    result = ExtractionResult(source_path=str(path))

    with pdfplumber.open(str(path)) as pdf:
        result.total_pages = len(pdf.pages)

        # Texte complet pour la detection des metadonnees globales
        full_text = ""

        for page in pdf.pages:
            pn = page.page_number

            # --- Tableaux ---
            tables = page.extract_tables()
            for table in tables:
                if not table or len(table) < 2:
                    continue
                headers = [str(c or "") for c in table[0]]
                rows = [[str(c or "") for c in row] for row in table[1:] if any(c for c in row)]
                if not rows:
                    continue
                result.table_elements.append(TableElement(
                    page_num=pn,
                    headers=headers,
                    rows=rows,
                    bbox=page.bbox,
                ))

            # --- Texte ---
            chars = page.chars
            if not chars:
                continue

            # Grouper les caracteres en lignes puis paragraphes
            lines = page.extract_text_lines()
            for line in lines:
                txt = line.get("text", "").strip()
                if not txt:
                    continue

                # Detecter les notes de bas de page
                if any(re.match(p, txt) for p in _FOOTNOTE_PATTERNS):
                    continue

                font_size = 12.0
                is_bold = False
                if line.get("chars"):
                    font_size = max(c.get("size", 12) for c in line["chars"])
                    is_bold = any(c.get("fontname", "").lower().find("bold") >= 0 for c in line["chars"])

                # Type d'element
                type_elem = "paragraph"
                if is_bold and font_size > 14:
                    type_elem = "title"
                elif is_bold or font_size > 13:
                    type_elem = "subtitle"

                result.text_elements.append(TextElement(
                    page_num=pn,
                    text=txt,
                    font_size=font_size,
                    is_bold=is_bold,
                    bbox=line.get("bbox"),
                    type=type_elem,
                ))
                full_text += " " + txt

        # Metadonnees globales
        result.titre_document = _detect_titre(full_text)
        result.organisme = _detect_organisme(full_text)
        result.periode_couverte = _detect_periode(full_text)
        result.date_publication = _detect_date_publication(full_text)

    return result
