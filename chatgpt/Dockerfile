# Use the official slim Python image
FROM python:3.12-slim AS builder

# Install system dependencies: Pandoc for conversion & build tools cleanup
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       pandoc \
       texlive-latex-base \
    && rm -rf /var/lib/apt/lists/*

# Create application directory
WORKDIR /app

# Copy and install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt  # includes requests & pypandoc :contentReference[oaicite:3]{index=3}

# Copy the converter script into the image
COPY arxiv_to_epub.py .

# Define entrypoint
ENTRYPOINT ["python", "arxiv_to_epub.py"]
CMD ["--help"]
