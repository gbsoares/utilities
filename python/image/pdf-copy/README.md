# PDF page duplication

Python script to take a given page on a pdf document and generate a new document with that page duplicated 'x' number of times.
It is particularly difficult to find a free tools or options to duplicate pdf pages...

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

```bash
python duplicate-page.py -i input.pdf -p 1 -n 4 -o output.pdf
```
