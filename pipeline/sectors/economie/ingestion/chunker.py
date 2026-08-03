"""
chunker.py — Decoupage structurel des elements extraits.

Regles :
  - Texte : decoupage par structure documentaire (titre > section > paragraphe)
            jamais de fenetre fixe. Cible 300-500 tokens, overlap 10-15%.
            Ne jamais couper une phrase ni separer un chiffre de son contexte.
  - Tableaux : chaque tableau = chunk autonome en Markdown.
               Grands tableaux : decoupage par blocs de lignes,
               en-tetes repetes dans chaque bloc.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Any

from .extractor import ExtractionResult, TextElement, TableElement


@dataclass
class Chunk:
    """Un chunk pret pour l'indexation."""
    doc_id: str
    chunk_index: int
    contenu: str
    type_contenu: str  # texte | tableau
    page_debut: int
    page_fin: int
    chapitre: str = ""
    section: str = ""
    contexte_prefix: str = ""
    tokens_estimes: int = 0


# ---------------------------------------------------------------------------
# Estimation de tokens (approximation : 4 caracteres = 1 token)
# ---------------------------------------------------------------------------
def _estimer_tokens(texte: str) -> int:
    return len(texte) // 4


def _format_tableau_markdown(table: TableElement, max_lignes: int | None = None) -> str:
    """Convertit un tableau en Markdown, avec option de troncature."""
    lignes = table.rows[:max_lignes] if max_lignes else table.rows
    if not lignes:
        return ""

    headers = table.headers
    # Ligne d'en-tete
    md = "| " + " | ".join(headers) + " |\n"
    md += "| " + " | ".join(["---"] * len(headers)) + " |\n"

    for row in lignes:
        md += "| " + " | ".join(str(c or "") for c in row) + " |\n"

    if table.title:
        md = f"*{table.title}*\n\n" + md
    if table.footnote:
        md += f"\n*{table.footnote}*"

    return md


# ---------------------------------------------------------------------------
# Chunking texte (structurel, pas de fenetre fixe)
# ---------------------------------------------------------------------------
def _chunker_texte(
    elements: list[TextElement],
    titre_doc: str,
    organisme: str,
) -> list[Chunk]:
    """Decoupe les elements textuels par structure documentaire."""
    chunks: list[Chunk] = []
    if not elements:
        return chunks

    # Phase 1 : detecter la structure (titres / sous-titres)
    sections: list[dict] = []
    current_section: dict = {"chapitre": "", "section": "", "elements": []}

    for elem in elements:
        if elem.type == "title":
            if current_section["elements"]:
                sections.append(current_section)
            current_section = {
                "chapitre": elem.text,
                "section": "",
                "elements": [],
            }
        elif elem.type == "subtitle":
            if current_section["elements"]:
                # Verifier si on a deja des elements -> nouvelle sous-section
                # Sinon, c'est le titre de la section courante
                pass
            current_section["section"] = elem.text
        else:
            current_section["elements"].append(elem)

    if current_section["elements"]:
        sections.append(current_section)

    # Phase 2 : grouper les paragraphes en chunks de 300-500 tokens
    idx = 0
    for sec in sections:
        chap = sec["chapitre"]
        sect = sec["section"]
        elems = sec["elements"]

        chunk_actuel: list[str] = []
        chunk_tokens = 0
        page_deb = elems[0].page_num if elems else 0

        for elem in elems:
            tok = _estimer_tokens(elem.text)

            # Si ajouter cet element depasse 500 tokens, finaliser le chunk
            if chunk_tokens + tok > 500 and chunk_tokens >= 300:
                contenu = " ".join(chunk_actuel)
                prefixe = f"[{organisme}, {titre_doc}]"
                chunks.append(Chunk(
                    doc_id="",
                    chunk_index=idx,
                    contenu=contenu,
                    type_contenu="texte",
                    page_debut=page_deb,
                    page_fin=elem.page_num,
                    chapitre=chap,
                    section=sect,
                    contexte_prefix=prefixe,
                    tokens_estimes=chunk_tokens,
                ))
                idx += 1
                # Chevauchement : garder les 10-15% derniers elements
                overlap_tokens = 0
                overlap_texts = []
                for prev in reversed(chunk_actuel):
                    t = _estimer_tokens(prev)
                    if overlap_tokens + t > chunk_tokens * 0.15:
                        break
                    overlap_tokens += t
                    overlap_texts.insert(0, prev)
                chunk_actuel = overlap_texts
                chunk_tokens = overlap_tokens
                page_deb = page_deb  # keep original page

            chunk_actuel.append(elem.text)
            chunk_tokens += tok

        # Dernier chunk de la section
        if chunk_actuel:
            contenu = " ".join(chunk_actuel)
            prefixe = f"[{organisme}, {titre_doc}]"
            chunks.append(Chunk(
                doc_id="",
                chunk_index=idx,
                contenu=contenu,
                type_contenu="texte",
                page_debut=page_deb,
                page_fin=elems[-1].page_num if elems else 0,
                chapitre=chap,
                section=sect,
                contexte_prefix=prefixe,
                tokens_estimes=chunk_tokens,
            ))
            idx += 1

    return chunks


# ---------------------------------------------------------------------------
# Chunking tableaux
# ---------------------------------------------------------------------------
def _chunker_tableaux(
    tables: list[TableElement],
    titre_doc: str,
    organisme: str,
) -> list[Chunk]:
    """Chaque tableau = un chunk autonome. Grands tableaux decoupes."""
    chunks: list[Chunk] = []
    MAX_LIGNES_PAR_BLOC = 15

    for table in tables:
        n_lignes = len(table.rows)
        if n_lignes <= MAX_LIGNES_PAR_BLOC:
            # Tableau entier
            md = _format_tableau_markdown(table)
            if md:
                prefixe = f"[{organisme}, {titre_doc}]"
                chunks.append(Chunk(
                    doc_id="",
                    chunk_index=0,
                    contenu=md,
                    type_contenu="tableau",
                    page_debut=table.page_num,
                    page_fin=table.page_num,
                    contexte_prefix=prefixe,
                    tokens_estimes=_estimer_tokens(md),
                ))
        else:
            # Decoupage par blocs avec en-tetes repetes
            n_blocs = math.ceil(n_lignes / MAX_LIGNES_PAR_BLOC)
            for b in range(n_blocs):
                debut = b * MAX_LIGNES_PAR_BLOC
                fin = min((b + 1) * MAX_LIGNES_PAR_BLOC, n_lignes)
                bloc = table.rows[debut:fin]
                md = _format_tableau_markdown(table)  # avec headers
                # Remplacer les lignes par le bloc courant
                md_lines = md.split("\n")
                header_part = "\n".join(md_lines[:2])  # header + separator
                body = "\n".join(
                    "| " + " | ".join(str(c or "") for c in row) + " |"
                    for row in bloc
                )
                md = f"{header_part}\n{body}"
                if table.title:
                    md = f"*{table.title} (suite {b+1}/{n_blocs})*\n\n{md}"
                prefixe = f"[{organisme}, {titre_doc}]"
                chunks.append(Chunk(
                    doc_id="",
                    chunk_index=0,
                    contenu=md,
                    type_contenu="tableau",
                    page_debut=table.page_num,
                    page_fin=table.page_num,
                    contexte_prefix=prefixe,
                    tokens_estimes=_estimer_tokens(md),
                ))

    return chunks


# ---------------------------------------------------------------------------
# Point d'entree principal
# ---------------------------------------------------------------------------
def chunk_document(
    extraction: ExtractionResult,
    doc_id: str = "",
) -> list[Chunk]:
    """
    Decoupe un document extrait en chunks structures.

    Retourne une liste de Chunk avec :
      - texte decoupe par structure documentaire
      - tableaux preserves en Markdown
      - contexte_prefix ajoute
    """
    if not doc_id:
        # Generer un doc_id depuis le nom de fichier
        import hashlib
        raw = extraction.source_path
        doc_id = f"{extraction.organisme.lower()}_{hashlib.md5(raw.encode()).hexdigest()[:8]}"

    # Chunking texte
    texte_chunks = _chunker_texte(
        extraction.text_elements,
        extraction.titre_document,
        extraction.organisme,
    )

    # Chunking tableaux
    table_chunks = _chunker_tableaux(
        extraction.table_elements,
        extraction.titre_document,
        extraction.organisme,
    )

    # Assembler et numeroter
    tous = texte_chunks + table_chunks
    for i, c in enumerate(tous):
        c.doc_id = doc_id
        c.chunk_index = i

    return tous
