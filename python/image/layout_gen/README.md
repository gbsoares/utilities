# Photo Layout Generator

A Python script that creates PDF layouts from JPEG images, arranging them in a customizable grid format.

## Features

- Automatically finds all JPEG images in a directory
- Rotates portrait images to landscape orientation
- Crops images to maintain aspect ratio
- Arranges images in a customizable grid layout
- Supports multiple page sizes (letter, A4, legal)
- High-quality image processing with configurable DPI

## Setup

### 1. Python Virtual Environment

Create a virtual environment and activate:

```bash
python3 -m venv venv
source venv/bin/activate
```

### Install Requirements

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run with default settings (4"×3" images, 2×3 grid, letter size):

```bash
python3 layout.py [-h] [-d INPUT_DIR] [-w WIDTH] [--height HEIGHT] [-m MARGIN] [-c COLS] [-r ROWS] [--dpi DPI] [-p {letter,A4,legal}] [-o OUTPUT]
```
