#!/usr/bin/env python3
"""
Script: arxiv_to_epub.py

Beschreibung:
Dieses Python-Skript lädt den LaTeX-Quellcode eines Papers von arXiv herunter und kompiliert ihn mithilfe von Pandoc zu einem EPUB-E-Book.

Voraussetzungen:
- Python 3.x
- pip install requests pypandoc
- Pandoc muss auf dem System installiert sein.

Benutzung:
    python arxiv_to_epub.py --id 2405.06128v1 --output paper.epub
    python arxiv_to_epub.py --id 2405.06128v1 --main main.tex --output paper.epub
"""
import argparse
import os
import sys
import tempfile
import tarfile
import zipfile
import requests
import pypandoc


def download_and_extract(arxiv_id, extract_dir):
    url = f"https://arxiv.org/e-print/{arxiv_id}"
    resp = requests.get(url, stream=True)
    resp.raise_for_status()

    # Temporäre Datei speichern
    tmp_path = os.path.join(extract_dir, f"{arxiv_id}.tar.gz")
    with open(tmp_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)

    # Entpacken
    try:
        with tarfile.open(tmp_path, "r:gz") as tar:
            tar.extractall(path=extract_dir)
    except tarfile.ReadError:
        # Vielleicht ZIP statt TAR
        with zipfile.ZipFile(tmp_path, 'r') as zipf:
            zipf.extractall(path=extract_dir)

    os.remove(tmp_path)
    return extract_dir

# Funktion zum Finden der Haupt-TeX-Datei
def find_main_tex(extract_dir, main_name=None):
    tex_files = []
    for root, _, files in os.walk(extract_dir):
        for fname in files:
            if fname.lower().endswith('.tex'):
                tex_files.append(os.path.join(root, fname))

    if not tex_files:
        raise FileNotFoundError("Keine .tex-Dateien gefunden im entpackten Verzeichnis.")
    if main_name:
        # Benutzerdefinierte Hauptdatei
        for path in tex_files:
            if os.path.basename(path) == main_name:
                return path
        raise FileNotFoundError(f"Hauptdatei '{main_name}' nicht gefunden.")
    # Falls nur eine .tex-Datei vorhanden ist
    if len(tex_files) == 1:
        return tex_files[0]
    # Mehrere .tex-Dateien: wähle die größte (Annahme: Hauptdatei)
    return max(tex_files, key=lambda p: os.path.getsize(p))

# Hauptfunktion
def main():
    parser = argparse.ArgumentParser(description='arXiv-LaTeX zu EPUB-Konverter')
    parser.add_argument('--id', required=True, help='arXiv-ID des Papers (z.B. 2405.06128v1)')
    parser.add_argument('--main', help='Name der Haupt-TeX-Datei (inkl. .tex)')
    parser.add_argument('--output', required=True, help='Zieldatei (.epub)')
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"Lade Quelldateien für arXiv-ID {args.id} herunter...")
        extract_dir = download_and_extract(args.id, tmpdir)

        print("Suche Haupt-TeX-Datei...")
        tex_path = find_main_tex(extract_dir, args.main)
        print(f"Gefundene Datei: {tex_path}")

        print(f"Konvertiere {tex_path} zu EPUB ({args.output})...")
        # Direkt mit pypandoc via pandoc
        pypandoc.convert_file(tex_path, 'epub', outputfile=args.output)

        print(f"Fertig! Dein EPUB wurde gespeichert als {args.output}.")

if __name__ == '__main__':
    main()
