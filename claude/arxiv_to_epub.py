#!/usr/bin/env python3
"""
arXiv to EPUB converter
This script downloads arXiv source files and converts them to EPUB format.
"""

import os
import sys
import re
import requests
import tarfile
import subprocess
import argparse
import shutil
import logging
from urllib.parse import urlparse
from pathlib import Path


class ArxivToEpub:
    def __init__(self, output_dir="./output", temp_dir="./temp"):
        """Initialize the converter with output and temporary directories."""
        self.output_dir = Path(output_dir)
        self.temp_dir = Path(temp_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self.temp_dir.mkdir(exist_ok=True, parents=True)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('arxiv2epub')
    
    def clean_up(self):
        """Remove temporary files."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            self.temp_dir.mkdir(exist_ok=True)
    
    def extract_arxiv_id(self, url_or_id):
        """Extract arXiv ID from URL or direct ID."""
        # Check if it's a URL or direct ID
        if url_or_id.startswith('http'):
            parsed_url = urlparse(url_or_id)
            path = parsed_url.path
            # Extract ID from URL using regex
            match = re.search(r'(?:abs|pdf)/(\d+\.\d+(?:v\d+)?)', path)
            if match:
                return match.group(1)
        else:
            # Assume it's a direct ID, validate format
            if re.match(r'^\d+\.\d+(?:v\d+)?$', url_or_id):
                return url_or_id
                
        raise ValueError("Invalid arXiv URL or ID format")
    
    def download_source(self, arxiv_id):
        """Download source files from arXiv."""
        self.logger.info(f"Downloading source for arXiv:{arxiv_id}")
        
        # Remove version from ID if present for source download
        base_id = re.sub(r'v\d+$', '', arxiv_id)
        
        # Construct the URL for the source files
        url = f"https://arxiv.org/e-print/{base_id}"
        
        # Download the source tarball
        response = requests.get(url, stream=True)
        if response.status_code != 200:
            raise Exception(f"Failed to download source: HTTP {response.status_code}")
        
        # Save the tarball
        tar_path = self.temp_dir / f"{arxiv_id}.tar.gz"
        with open(tar_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Extract the tarball
        paper_dir = self.temp_dir / arxiv_id
        paper_dir.mkdir(exist_ok=True)
        
        try:
            with tarfile.open(tar_path, "r:gz") as tar:
                tar.extractall(path=paper_dir)
        except tarfile.ReadError:
            # Try with plain tar (some arXiv sources aren't gzipped)
            try:
                with tarfile.open(tar_path, "r:") as tar:
                    tar.extractall(path=paper_dir)
            except Exception as e:
                self.logger.error(f"Could not extract archive: {e}")
                raise
        
        return paper_dir
    
    def find_main_tex_file(self, paper_dir):
        """Find the main TeX file in the paper directory."""
        # Look for typical main file names
        common_names = ["main.tex", "paper.tex", "manuscript.tex", "article.tex", "arxiv.tex"]
        
        for name in common_names:
            tex_file = paper_dir / name
            if tex_file.exists():
                self.logger.info(f"Found main TeX file by common name: {tex_file}")
                return tex_file
        
        # Look for files with \begin{document}
        for tex_file in paper_dir.glob("*.tex"):
            try:
                with open(tex_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if r'\begin{document}' in content:
                        self.logger.info(f"Found main TeX file by document tag: {tex_file}")
                        return tex_file
            except Exception as e:
                self.logger.warning(f"Error reading {tex_file}: {e}")
        
        # If still not found, just return the first .tex file
        tex_files = list(paper_dir.glob("*.tex"))
        if tex_files:
            self.logger.info(f"Using first available TeX file: {tex_files[0]}")
            return tex_files[0]
        
        raise FileNotFoundError("No TeX files found in the downloaded source")
    
    def preprocess_tex_file(self, tex_file):
        """Preprocess the TeX file to make it more pandoc-friendly."""
        self.logger.info(f"Preprocessing {tex_file}")
        
        # Create a backup
        backup_file = tex_file.with_suffix('.tex.bak')
        shutil.copy2(tex_file, backup_file)
        
        try:
            with open(tex_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Replace problematic LaTeX commands that pandoc has trouble with
            modified_content = content
            
            # Remove or simplify \cite commands
            modified_content = re.sub(r'\\cite\{([^}]*)\}', r'[\\1]', modified_content)
            
            # Simplify other common problematic commands
            replacements = [
                (r'\\includegraphics(\[[^\]]*\])?\{([^}]*)\}', r'[Image: \2]'),  # Replace image references
                (r'\\ref\{([^}]*)\}', r'[ref]'),  # Replace cross-references
                (r'\\label\{([^}]*)\}', r''),  # Remove labels
                (r'\\input\{([^}]*)\}', r'% Input file: \1'),  # Comment out input commands
                (r'\\include\{([^}]*)\}', r'% Include file: \1'),  # Comment out include commands
                (r'\\bibliography\{([^}]*)\}', r'% Bibliography: \1'),  # Comment out bibliography
                (r'\\bibliographystyle\{([^}]*)\}', r''),  # Remove bibliography style
            ]
            
            for pattern, replacement in replacements:
                modified_content = re.sub(pattern, replacement, modified_content)
            
            # Write the modified content back
            with open(tex_file, 'w', encoding='utf-8') as f:
                f.write(modified_content)
                
            return True
        
        except Exception as e:
            self.logger.error(f"Error preprocessing TeX file: {e}")
            # Restore the backup if something went wrong
            shutil.copy2(backup_file, tex_file)
            return False
    
    def create_simple_cover(self, paper_dir, arxiv_id):
        """Create a very simple text-based cover file."""
        cover_path = paper_dir / "cover.html"
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>arXiv:{arxiv_id}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            text-align: center;
            margin-top: 40%;
        }}
        h1 {{
            font-size: 24pt;
        }}
    </style>
</head>
<body>
    <h1>arXiv: {arxiv_id}</h1>
</body>
</html>
"""
        
        with open(cover_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        return cover_path
    
    def create_cover_image(self, paper_dir, arxiv_id):
        """Create a simple cover image with arXiv ID."""
        # First try using ImageMagick
        try:
            cover_path = paper_dir / "cover.png"
            
            cmd = [
                "convert",
                "-size", "600x800",
                "xc:white",
                "-gravity", "center",
                "-pointsize", "42",
                "-annotate", "+0+0", f"arXiv:{arxiv_id}",
                str(cover_path)
            ]
            
            self.logger.info("Attempting to create cover image with ImageMagick")
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            if cover_path.exists():
                self.logger.info("Successfully created cover image")
                return cover_path
                
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            self.logger.warning(f"Could not create cover image with ImageMagick: {e}")
        
        # Fallback: create a simple HTML cover
        self.logger.info("Creating fallback HTML cover")
        return self.create_simple_cover(paper_dir, arxiv_id)
    
    def convert_to_epub(self, tex_file, arxiv_id):
        """Convert TeX file to EPUB using pandoc."""
        self.logger.info(f"Converting {tex_file.name} to EPUB")
        
        # Output EPUB path
        epub_path = self.output_dir / f"{arxiv_id}.epub"
        
        # Preprocess the TeX file to improve conversion reliability
        if not self.preprocess_tex_file(tex_file):
            self.logger.warning("TeX preprocessing failed, attempting conversion anyway")
        
        # Change to the directory containing the TeX file for proper resolution of includes
        original_dir = os.getcwd()
        os.chdir(tex_file.parent)
        
        # Create a cover
        cover_path = self.create_cover_image(tex_file.parent, arxiv_id)
        cover_option = []
        
        if cover_path:
            if cover_path.suffix == '.png':
                cover_option = ["--epub-cover-image=" + cover_path.name]
            elif cover_path.suffix == '.html':
                cover_option = ["--epub-cover-html=" + cover_path.name]
        
        try:
            # First try a simple conversion with minimal options
            cmd = [
                "pandoc",
                "-s",
                tex_file.name,
                "-o", str(epub_path),
                "--toc",
                "-f", "latex",
                "-t", "epub"
            ] + cover_option
            
            self.logger.info(f"Running pandoc with command: {' '.join(cmd)}")
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            self.logger.info(f"Successfully created EPUB at {epub_path}")
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Pandoc conversion failed: {e.stderr}")
            
            # More aggressive fallback: try converting to markdown first, then to EPUB
            try:
                self.logger.info("Trying two-step conversion via markdown")
                
                # First convert to markdown
                md_file = tex_file.with_suffix('.md')
                md_cmd = [
                    "pandoc",
                    "-s",
                    tex_file.name,
                    "-o", md_file.name,
                    "-f", "latex",
                    "-t", "markdown"
                ]
                
                subprocess.run(md_cmd, check=True, capture_output=True, text=True)
                
                # Then convert markdown to EPUB
                epub_cmd = [
                    "pandoc",
                    "-s",
                    md_file.name,
                    "-o", str(epub_path),
                    "--toc",
                    "-f", "markdown",
                    "-t", "epub"
                ] + cover_option
                
                subprocess.run(epub_cmd, check=True, capture_output=True, text=True)
                self.logger.info(f"Two-step conversion successful: {epub_path}")
                
            except subprocess.CalledProcessError as e2:
                self.logger.error(f"All conversion attempts failed: {e2.stderr}")
                os.chdir(original_dir)
                raise Exception("Failed to convert TeX to EPUB")
        
        # Return to original directory
        os.chdir(original_dir)
        return epub_path
    
    def process_paper(self, arxiv_url_or_id):
        """Process an arXiv paper: download, extract, and convert to EPUB."""
        try:
            # Extract arXiv ID
            arxiv_id = self.extract_arxiv_id(arxiv_url_or_id)
            self.logger.info(f"Processing arXiv ID: {arxiv_id}")
            
            # Download the source files
            paper_dir = self.download_source(arxiv_id)
            
            # Find the main TeX file
            main_tex = self.find_main_tex_file(paper_dir)
            self.logger.info(f"Found main TeX file: {main_tex}")
            
            # Convert to EPUB
            epub_path = self.convert_to_epub(main_tex, arxiv_id)
            
            return epub_path
            
        except Exception as e:
            self.logger.error(f"Error processing {arxiv_url_or_id}: {str(e)}")
            return None
        finally:
            self.clean_up()


def main():
    parser = argparse.ArgumentParser(description="Convert arXiv papers to EPUB format")
    parser.add_argument("arxiv_id", help="arXiv ID or URL (e.g., 2103.13630 or https://arxiv.org/abs/2103.13630)")
    parser.add_argument("-o", "--output-dir", default="./output", help="Output directory for EPUB files")
    parser.add_argument("-t", "--temp-dir", default="./temp", help="Temporary directory for processing")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    # Set logging level based on verbose flag
    if args.verbose:
        logging.getLogger('arxiv2epub').setLevel(logging.DEBUG)
    
    converter = ArxivToEpub(output_dir=args.output_dir, temp_dir=args.temp_dir)
    epub_path = converter.process_paper(args.arxiv_id)
    
    if epub_path:
        print(f"Conversion complete: {epub_path}")
    else:
        print("Conversion failed")
        sys.exit(1)


if __name__ == "__main__":
    main()