## arxiv-to-epub

A simple Python tool that downloads the LaTeX source of an arXiv e-print and converts it into an EPUB e-book using Pandoc. It automates fetching via arXiv’s e-print interface, extracts the archive, identifies the main `.tex` file, and invokes Pandoc through the `pypandoc` wrapper to produce a clean, readable EPUB suitable for e-readers.

---

## Features

- **Automated Source Retrieval**  
  Fetches the LaTeX source archive directly from arXiv via `https://arxiv.org/e-print/{ID}`  ([arXiv API Basics](https://info.arxiv.org/help/api/basics.html?utm_source=chatgpt.com)).  
- **Archive Extraction**  
  Handles both `.tar.gz` and `.zip` packages for maximum compatibility  ([About READMEs - GitHub Docs](https://docs.github.com/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes?utm_source=chatgpt.com)).  
- **Main `.tex` Detection**  
  Automatically selects the primary TeX file (by filename or largest size) to simplify multi-file projects.  
- **EPUB Conversion**  
  Uses `pypandoc` as a thin Python wrapper around Pandoc to generate EPUB output  ([JessicaTegner/pypandoc: Thin wrapper for "pandoc" (MIT) - GitHub](https://github.com/JessicaTegner/pypandoc?utm_source=chatgpt.com), [Creating an ebook with pandoc](https://pandoc.org/epub.html?utm_source=chatgpt.com)).  

---

## Prerequisites

1. **Python 3.x**  
2. **Pandoc** installed on your system (version ≥ 1.6 for EPUB support)  ([Creating an ebook with pandoc](https://pandoc.org/epub.html?utm_source=chatgpt.com)).  
3. **Python packages**:  
   ```bash
   pip install requests pypandoc
   ```  
   - `requests` for HTTP downloads  ([About READMEs - GitHub Docs](https://docs.github.com/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes?utm_source=chatgpt.com))  
   - `pypandoc` for interfacing with Pandoc  ([JessicaTegner/pypandoc: Thin wrapper for "pandoc" (MIT) - GitHub](https://github.com/JessicaTegner/pypandoc?utm_source=chatgpt.com))  

---

## Installation

Clone this repository and ensure dependencies are met:

```bash
git clone https://github.com/yourusername/arxiv-to-epub.git
cd arxiv-to-epub
pip install requests pypandoc
```

> **Tip:** If you’d rather have Pandoc bundled, consider installing `pypandoc_binary` instead of `pypandoc`  ([https://raw.githubusercontent.com/bebraw/pypandoc/...](https://raw.githubusercontent.com/bebraw/pypandoc/master/README.md?utm_source=chatgpt.com)).

---

## Usage

```bash
python arxiv_to_epub.py --id <ARXIV_ID> --output <OUTPUT_FILE.epub>
```

- `--id` (required): arXiv identifier (e.g., `2405.06128v1`)  ([arXiv API Basics](https://info.arxiv.org/help/api/basics.html?utm_source=chatgpt.com)).  
- `--output` (required): target EPUB filename.  
- `--main` (optional): specify the main `.tex` filename if auto-detection fails.

Example:

```bash
python arxiv_to_epub.py --id 2405.06128v1 --output mypaper.epub
```

---

## Command-Line Options

| Option           | Description                                               |
|------------------|-----------------------------------------------------------|
| `--id`           | **(Required)** arXiv e-print ID, including version (e.g., `2101.12345v2`). |
| `--output`       | **(Required)** Name of the EPUB file to generate.         |
| `--main`         | (Optional) Filename of the primary `.tex` file.           |

---

## Contributing

Contributions are welcome! Please follow these guidelines:

- Fork the repository.  
- Create a feature branch (`git checkout -b feature-name`).  
- Commit your changes (`git commit -m 'Add feature'`).  
- Push to the branch (`git push origin feature-name`).  
- Open a Pull Request.

For writing clear documentation, see “[Best practices for writing a README](https://github.com/jehna/readme-best-practices)”  ([jehna/readme-best-practices - GitHub](https://github.com/jehna/readme-best-practices?utm_source=chatgpt.com)) and GitHub’s official “[About READMEs](https://docs.github.com/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)”  ([About READMEs - GitHub Docs](https://docs.github.com/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes?utm_source=chatgpt.com)).

---

## License

This project is released under the **MIT License**. See [LICENSE](LICENSE) for details.

---

## Acknowledgments

- **Pandoc** – Universal document converter  ([Creating an ebook with pandoc](https://pandoc.org/epub.html?utm_source=chatgpt.com)).  
- **pypandoc** – Thin Python wrapper for Pandoc  ([JessicaTegner/pypandoc: Thin wrapper for "pandoc" (MIT) - GitHub](https://github.com/JessicaTegner/pypandoc?utm_source=chatgpt.com)).  
- **arXiv** – Open access e-print repository  ([arXiv API User's Manual](https://info.arxiv.org/help/api/user-manual.html?utm_source=chatgpt.com), [arXiv API Access](https://info.arxiv.org/help/api/index.html?utm_source=chatgpt.com)).  