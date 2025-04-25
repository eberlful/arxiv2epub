# Use a base image with TeX Live and Python
FROM ubuntu:22.04

# Avoid prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install required packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-science \
    pandoc \
    imagemagick \
    wget \
    curl \
    ghostscript \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app

# Copy the script and requirements
COPY arxiv_to_epub.py /app/
COPY requirements.txt /app/

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Create output directory
RUN mkdir -p /app/output /app/temp

# Set permissions
RUN chmod +x /app/arxiv_to_epub.py

# Fix ImageMagick policy to allow PDF operations
RUN if [ -f /etc/ImageMagick-6/policy.xml ]; then \
        sed -i 's/rights="none" pattern="PDF"/rights="read|write" pattern="PDF"/' /etc/ImageMagick-6/policy.xml; \
    fi

# If using ImageMagick 7, we need to modify this file instead
RUN if [ -f /etc/ImageMagick/policy.xml ]; then \
        sed -i 's/rights="none" pattern="PDF"/rights="read|write" pattern="PDF"/' /etc/ImageMagick/policy.xml; \
    fi

# Set the entrypoint to the Python script
ENTRYPOINT ["python3", "/app/arxiv_to_epub.py"]

# Default command (can be overridden)
CMD ["--help"]