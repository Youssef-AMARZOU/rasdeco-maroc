"""
metadata.py — Enrichissement contextuel et generation des metadonnees.

Pour chaque chunk :
  - Genere le contexte_prefix (titre document, chapitre, section)
  - Extrait la periode_couverte depuis le texte
  - Calcule le checksum SHA256 du chunk
  - Produit le dictionnaire de metadonnees final

Format de sortie par chunk :
```json
{
  "doc_id": "...",
  "titre_document": "...",
  "organisme": "BAM",
  "date_publication": "2020-06-30",
  "periode_couverte": "2019",
  "page_debut": 87, "page_fin": 88,
  "chapitre": "Politique monetaire",
  "section": "4.2 Decisions du Conseil",
  "type_contenu": "tableau | texte",
  "langue": "fr",
  "checksum_source": "sha256...",
  "contenu": "...",
  "tokens_estimes": 412
}
```
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from .chunker import Chunk
from .extractor import ExtractionResult


def _calculer_checksum(texte: str) -> str:
    return hashlib.sha256(texte.encode("utf-8")).hexdigest()


def _extraire_periode(texte: str, extraction: ExtractionResult) -> str:
    """Extrait la periode couverte par le chunk (priorite au document)."""
    if extraction.periode_couverte:
        return extraction.periode_couverte

    # Fallback : chercher une annee dans le texte du chunk
    for pat in [r"(20[0-9]{2})\s*[-u2013]\s*(20[0-9]{2})",
                r"(20[0-9]{2})"]:
        m = re.search(pat, texte)
        if m:
            return m.group(0)
    return ""


def enrichir_chunk(
    chunk: Chunk,
    extraction: ExtractionResult,
    idx: int,
) -> dict[str, Any]:
    """
    Enrichit un chunk avec toutes les metadonnees necessaires.

    Retourne un dictionnaire pret pour le JSONL.
    """
    # Reconstruire le contexte_prefix si vide
    if not chunk.contexte_prefix:
        parties = [f"[{extraction.organisme}, {extraction.titre_document}]"]
        if chunk.chapitre:
            parties.append(chunk.chapitre)
        if chunk.section:
            parties.append(chunk.section)
        chunk.contexte_prefix = " > ".join(parties)

    # Detectar la langue (texte majoritairement francais)
    langue = "fr"
    if re.search(r"[aeiouy]+", chunk.contenu[:100], re.IGNORECASE):
        langue = "fr"

    return {
        "doc_id": chunk.doc_id,
        "chunk_index": chunk.chunk_index,
        "contenu": chunk.contenu,
        "contexte_prefix": chunk.contexte_prefix,
        "titre_document": extraction.titre_document,
        "organisme": extraction.organisme,
        "date_publication": extraction.date_publication,
        "periode_couverte": _extraire_periode(chunk.contenu, extraction),
        "page_debut": chunk.page_debut,
        "page_fin": chunk.page_fin,
        "chapitre": chunk.chapitre,
        "section": chunk.section,
        "type_contenu": chunk.type_contenu,
        "langue": langue,
        "tokens_estimes": chunk.tokens_estimes,
        "checksum_source": _calculer_checksum(chunk.contenu),
    }


def produire_jsonl(
    chunks: list[Chunk],
    extraction: ExtractionResult,
    output_path: str | Path,
) -> int:
    """
    Produit un fichier JSONL avec les chunks enrichis.

    Retourne le nombre de chunks ecrits.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        for idx, chunk in enumerate(chunks):
            record = enrichir_chunk(chunk, extraction, idx)
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return len(chunks)
