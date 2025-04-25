# arXiv to EPUB Converter

A tool to download and convert arXiv papers from their original LaTeX sources to EPUB format for better reading experience on e-readers and mobile devices.

## Features

- Download arXiv source files using arXiv ID or URL
- Automatically identify the main TeX file
- Convert TeX documents to EPUB format with Pandoc
- Generate basic cover images for converted papers
- Docker support for easy usage without local installation

## Prerequisites

If running without Docker, you'll need:

- Python 3.6+
- Pandoc
- A working LaTeX installation (TeX Live recommended)
- ImageMagick (optional, for cover image generation)

## Installation

### Using Docker (Recommended)

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/arxiv-to-epub.git
   cd arxiv-to-epub
   ```

2. Build the Docker image:
   ```
   docker build -t arxiv-to-epub .
   ```

### Manual Installation

1. Install the required system packages:
   ```
   # Debian/Ubuntu
   sudo apt-get install texlive-latex-base texlive-latex-extra texlive-fonts-recommended texlive-science pandoc imagemagick
   
   # Fedora
   sudo dnf install texlive-scheme-basic texlive-latex texlive-collection-science pandoc ImageMagick
   
   # macOS (using Homebrew)
   brew install texlive pandoc imagemagick
   ```

2. Install Python requirements:
   ```
   pip install -r requirements.txt
   ```

## Usage

### With Docker

```bash
# Create a local output directory
mkdir -p output

# Convert a paper by ID
docker run -v "$(pwd)/output:/app/output" arxiv-to-epub 2103.13630

# Convert a paper by URL
docker run -v "$(pwd)/output:/app/output" arxiv-to-epub https://arxiv.org/abs/2103.13630

# Specify output directory
docker run -v "$(pwd)/custom_output:/app/output" arxiv-to-epub -o /app/output 2103.13630
```

### Without Docker

```bash
# Convert a paper by ID
python arxiv_to_epub.py 2103.13630

# Convert a paper by URL
python arxiv_to_epub.py https://arxiv.org/abs/2103.13630

# Specify output directory
python arxiv_to_epub.py -o ./my_books 2103.13630
```

## Command Line Options

```
usage: arxiv_to_epub.py [-h] [-o OUTPUT_DIR] [-t TEMP_DIR] arxiv_id

Convert arXiv papers to EPUB format

positional arguments:
  arxiv_id              arXiv ID or URL (e.g., 2103.13630 or https://arxiv.org/abs/2103.13630)

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Output directory for EPUB files
  -t TEMP_DIR, --temp-dir TEMP_DIR
                        Temporary directory for processing
```

## Limitations

- Complex LaTeX documents with specialized packages may not convert perfectly
- Mathematical formulas rendering quality depends on Pandoc's capabilities
- Some arXiv papers might use custom macros or packages that aren't supported

## Troubleshooting

### EPUB creation fails

If the conversion fails, try these steps:

1. Make sure you have all the required LaTeX packages installed
2. Check if the arXiv source contains unusual or custom LaTeX packages
3. Try increasing the Docker container's memory if you're getting out-of-memory errors

### Missing images in EPUB

Some papers might reference images in ways that Pandoc can't properly resolve. In these cases:

1. Download the source manually
2. Fix the image references
3. Run the conversion tool on the fixed source

## License

MIT License