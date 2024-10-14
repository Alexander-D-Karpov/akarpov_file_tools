#!/bin/bash

set -e

apt-get update
apt-get install -y \
    libnotify4 \
    scribus \
    libappindicator3-1 \
    libayatana-indicator3-7 \
    libdbusmenu-glib4 \
    libdbusmenu-gtk3-4 \
    poppler-utils \
    libfile-mimeinfo-perl \
    ghostscript \
    libsecret-1-0 \
    imagemagick \
    libmagic1 \
    libreoffice \
    inkscape \
    xvfb \
    libxml2-dev \
    libxslt1-dev \
    antiword \
    unrtf \
    tesseract-ocr \
    flac \
    lame \
    libmad0 \
    libsox-fmt-mp3 \
    sox \
    swig \
    python-dev-is-python3 \
    ffmpeg \
    libcairo2-dev \
    libgirepository1.0-dev

# Install draw.io
wget https://github.com/jgraph/drawio-desktop/releases/download/v13.0.3/draw.io-amd64-13.0.3.deb
dpkg -i draw.io-amd64-13.0.3.deb
rm draw.io-amd64-13.0.3.deb

# Clean up
apt-get clean
rm -rf /var/lib/apt/lists/*

# Install additional Python packages
pip install --no-cache-dir \
    python-magic \
    Pillow \
    textract \
    rawpy \
    xvfbwrapper \
    vtk \
    cairosvg \
    ffmpeg-python

# Check preview-generator dependencies
preview --check-dependencies