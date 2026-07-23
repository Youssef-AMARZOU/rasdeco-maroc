"""
pipeline_ingestion.py — Orchestrateur du pipeline d'ingestion.

Enchaine :
  1. Extraction PDF (texte + tableaux)  -> extractor.py
  2. Chunking structurel                -> chunker.py
  3. Enrichissement metadonnees         -> metadata.py
  4. Sortie JSONL pour indexation

Usage :
    python -m economie.ingestion.pipeline_ingestion chemin/vers/rapport.pdf -o output/
    python -m economie.ingestion.pipeline_ingestion dossier/ --recursive -o output/
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from .extractor import extract_pdf
from .chunker import chunk_document
from .metadata import produire_jsonl


def process_pdf(
    pdf_path: str | Path,
    output_dir: str | Path = "data/indexed/",
    doc_id: str = "",
) -> dict:
    """
    Traite un fichier PDF unique.

    Parametres
    ----------
    pdf_path : chemin du PDF
    output_dir : repertoire de sortie pour le JSONL
    doc_id : identifiant unique du document (optionnel)

    Retourne
    --------
    dict avec le rapport de traitement (statuts, nombre chunks, duree)
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        return {"status": "error", "message": f"Fichier introuvable : {pdf_path}"}

    t0 = time.time()

    # 1. Extraction
    print(f"  Extraction : {pdf_path.name}...")
    extraction = extract_pdf(pdf_path)
    n_text = len(extraction.text_elements)
    n_tables = len(extraction.table_elements)
    print(f"    -> {n_text} elements texte, {n_tables} tableaux")

    # 2. Chunking
    print(f"  Chunking...")
    if not doc_id:
        doc_id = f"{extraction.organisme.lower()}_{pdf_path.stem}" if extraction.organisme else pdf_path.stem
    chunks = chunk_document(extraction, doc_id=doc_id)
    print(f"    -> {len(chunks)} chunks (texte: {sum(1 for c in chunks if c.type_contenu == 'texte')}, tableau: {sum(1 for c in chunks if c.type_contenu == 'tableau')})")

    # 3. Metadonnees + ecriture JSONL
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{pdf_path.stem}.chunks.jsonl"

    n_chunks = produire_jsonl(chunks, extraction, output_path)
    elapsed = time.time() - t0

    # Ecrire aussi un rapport JSON
    rapport = {
        "status": "ok",
        "source": str(pdf_path),
        "doc_id": doc_id,
        "organisme": extraction.organisme,
        "titre": extraction.titre_document,
        "periode_couverte": extraction.periode_couverte,
        "pages": extraction.total_pages,
        "elements_texte": n_text,
        "elements_tableaux": n_tables,
        "total_chunks": n_chunks,
        "output": str(output_path),
        "duree_s": round(elapsed, 2),
    }

    rapport_path = output_dir / f"{pdf_path.stem}.report.json"
    with open(rapport_path, "w", encoding="utf-8") as f:
        json.dump(rapport, f, ensure_ascii=False, indent=2)

    print(f"  Termine : {n_chunks} chunks -> {output_path} ({elapsed:.1f}s)")
    return rapport


def process_directory(
    dir_path: str | Path,
    output_dir: str | Path = "data/indexed/",
    recursive: bool = False,
) -> list[dict]:
    """
    Traite tous les PDF d'un repertoire.

    Parametres
    ----------
    dir_path : repertoire contenant les PDF
    output_dir : repertoire de sortie
    recursive : parcourir les sous-repertoires

    Retourne
    --------
    liste des rapports individuels
    """
    dir_path = Path(dir_path)
    if not dir_path.exists():
        print(f"ERREUR : dossier introuvable {dir_path}")
        return []

    pattern = "**/*.pdf" if recursive else "*.pdf"
    pdfs = sorted(dir_path.glob(pattern))

    if not pdfs:
        print(f"Aucun PDF trouve dans {dir_path}")
        return []

    print(f"Traitement de {len(pdfs)} PDF dans {dir_path}")
    rapports = []

    for pdf in pdfs:
        r = process_pdf(pdf, output_dir=output_dir)
        rapports.append(r)

    # Rapport synthetique
    ok = sum(1 for r in rapports if r.get("status") == "ok")
    total_chunks = sum(r.get("total_chunks", 0) for r in rapports if r.get("status") == "ok")
    duree = sum(r.get("duree_s", 0) for r in rapports if r.get("status") == "ok")

    print(f"\n{'='*50}")
    print(f"Traitement termine : {ok}/{len(pdfs)} OK, {total_chunks} chunks, {duree:.1f}s")
    print(f"Sortie : {Path(output_dir).resolve()}")

    return rapports


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Pipeline d'ingestion PDF -> chunks indexes (RASD-Maroc)"
    )
    parser.add_argument("input", help="Fichier PDF ou dossier")
    parser.add_argument("-o", "--output-dir", default="data/indexed/",
                        help="Repertoire de sortie (defaut: data/indexed/)")
    parser.add_argument("-r", "--recursive", action="store_true",
                        help="Parcourir les sous-dossiers (mode dossier)")
    parser.add_argument("--doc-id", default="",
                        help="Identifiant du document (optionnel)")
    args = parser.parse_args()

    input_path = Path(args.input)
    if input_path.is_dir():
        process_directory(input_path, args.output_dir, args.recursive)
    else:
        process_pdf(input_path, args.output_dir, args.doc_id)


if __name__ == "__main__":
    main()
