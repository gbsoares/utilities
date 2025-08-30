# HEIC Converter

## Setup Instructions

### 1. Create a Python Virtual Environment

```bash
python3 -m venv venv
```

### 2. Activate the Virtual Environment

- **On Linux/macOS:**

```bash
source venv/bin/activate
```

### 3. Install Requirements

Install python requirements:

```bash
pip install -r requirements.txt
```

You may also need to install HEIF/AVIF encoder and decoder library:
```bash
sudo apt install libheif1
```

### 4. Run the Script

```bash
python heic.py [-d DIRECTORY] [-f {JPEG,JPG,PNG,WEBP}] [--delete-original] [--no-parallel]
```
