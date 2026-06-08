# Python Virtual Environment Setup Guide

This guide provides step-by-step instructions for setting up a Python virtual environment to run the Phaser notebooks.

**Tested on:** Python 3.12

---

## Prerequisites

- **Python 3.12** (or compatible version 3.10+)
- **pip** (Python package manager)
- **Git** (for version control)
- **Git LFS** (for large media files - videos, images)

### Install Git LFS

**Windows (Chocolatey):**
```powershell
choco install git-lfs
```

**Windows (Manual):**
Download from https://git-lfs.com and run the installer.

**Linux/macOS (Homebrew):**
```bash
brew install git-lfs
```

**Linux (APT):**
```bash
sudo apt-get install git-lfs
```

**After Installation:**
```bash
git lfs install
```

---

## Verify Your Python Version:

**Windows:**
```powershell
py --list
py -3.12 --version
```

**Linux/macOS:**
```bash
python3.12 --version
```

---

## Setup Instructions

### 1. Create Virtual Environment

Navigate to the project directory and create a version-specific virtual environment:

**Windows (using Python launcher):**
```powershell
cd "c:\ADI Repo\Phaser"
py -3.12 -m venv .venv3.12
```

**Linux/macOS:**
```bash
cd ~/ADI\ Repo/Phaser
python3.12 -m venv .venv3.12
```

This creates a new folder `.venv3.12/` containing an isolated Python 3.12 environment. The version-specific naming allows you to maintain multiple Python versions if needed.

### 2. Activate Virtual Environment

#### On Windows (PowerShell):
```powershell
.\.venv3.12\Scripts\Activate.ps1
```

If you encounter an execution policy error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try activating again.

#### On Windows (Command Prompt):
```cmd
.\.venv3.12\Scripts\activate.bat
```

#### On Linux/macOS:
```bash
source .venv3.12/bin/activate
```

**Expected output:** Your prompt will change to show `(venv3.12)` prefix:

Windows:
```
(.venv3.12) PS C:\ADI Repo\Phaser>
```

Linux/macOS:
```
(.venv3.12) user@hostname:~/ADI Repo/Phaser$
```

### 3. Upgrade pip (Optional but Recommended)

**Windows:**
```powershell
py -3.12 -m pip install --upgrade pip
```

**Linux/macOS:**
```bash
python3.12 -m pip install --upgrade pip
```

### 4. Install Dependencies

Install all required packages from `requirements.txt`:

**Windows:**
```powershell
pip install -r requirements.txt
```

**Linux/macOS:**
```bash
pip install -r requirements.txt
```

This will install:
- Scientific computing (numpy, scipy, matplotlib, pandas)
- Jupyter environment (jupyter, ipykernel, ipywidgets)
- ADI hardware interface (pyadi-iio)
- Animation tools (manim)
- Git integration (GitPython)

### 5. Launch Jupyter Notebook

Start the Jupyter notebook server:

**Windows:**
```powershell
jupyter notebook
```

**Linux/macOS:**
```bash
jupyter notebook
```

Or use Jupyter Lab (if preferred):

**Windows:**
```powershell
jupyter lab
```

**Linux/macOS:**
```bash
jupyter lab
```

This will open your default web browser to the Jupyter interface. Navigate to the tutorial notebooks:
- `beam-forming-tutorials/` - Phaser basics and beamforming
- `radar-tutorials/` - FMCW radar demonstrations
- `phaser-setup/` - Hardware setup guide

---

## Deactivating Virtual Environment

When finished, deactivate the virtual environment (same command for all platforms):

```bash
deactivate
```

Your prompt will return to normal (no `(.venv3.12)` prefix).

---

## Troubleshooting

### Issue: "PowerShell ExecutionPolicy" Error

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: `venv` module not found

**Solution:** Ensure Python is properly installed:

**Windows:**
```powershell
py -3.12 -m ensurepip --upgrade
```

**Linux/macOS:**
```bash
python3.12 -m ensurepip --upgrade
```

### Issue: `libiio` installation fails (Windows)

**Solution:** Use conda instead of pip:
```powershell
conda install libiio
```

Or install via Chocolatey:
```powershell
choco install libiio
```

**Linux/macOS Solution:**
```bash
# Ubuntu/Debian
sudo apt-get install libiio0

# macOS (using Homebrew)
brew install libiio
```

### Issue: `manim` requires ffmpeg

**Solution (Windows):** Install ffmpeg via Chocolatey:
```powershell
choco install ffmpeg
```

**Solution (Linux/macOS):**
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS (using Homebrew)
brew install ffmpeg
```

Or download from: https://ffmpeg.org/download.html

### Issue: Jupyter kernel not found in notebook

**Solution:** Install ipykernel in your venv:

**Windows:**
```powershell
pip install ipykernel
py -3.12 -m ipykernel install --user --name phaser --display-name "Python (Phaser)"
```

**Linux/macOS:**
```bash
pip install ipykernel
python3.12 -m ipykernel install --user --name phaser --display-name "Python (Phaser)"
```

---

## Verify Installation

To verify everything is installed correctly, run:

**Windows:**
```powershell
py -3.12 -c "import numpy, scipy, matplotlib, jupyter, pyadi_iio; print('All packages installed successfully!')"
```

**Linux/macOS:**
```bash
python3.12 -c "import numpy, scipy, matplotlib, jupyter, pyadi_iio; print('All packages installed successfully!')"
```

---

## Quick Reference Commands

### Windows (PowerShell)

| Task | Command |
|------|---------|
| Activate venv | `.\.venv3.12\Scripts\Activate.ps1` |
| Deactivate venv | `deactivate` |
| Install requirements | `pip install -r requirements.txt` |
| Start Jupyter | `jupyter notebook` |
| Check Python version | `py -3.12 --version` |
| List installed packages | `pip list` |
| Update pip | `py -3.12 -m pip install --upgrade pip` |

### Linux/macOS

| Task | Command |
|------|---------|
| Activate venv | `source .venv3.12/bin/activate` |
| Deactivate venv | `deactivate` |
| Install requirements | `pip install -r requirements.txt` |
| Start Jupyter | `jupyter notebook` |
| Check Python version | `python3.12 --version` |
| List installed packages | `pip list` |
| Update pip | `python3.12 -m pip install --upgrade pip` |

---

## Notes

- **Git LFS:** This repository uses Git LFS to efficiently manage large media files (videos, images, audio). All video files (.mp4), images (.png, .jpg, .gif), and other large media are stored via LFS.
- **Project Structure:** Keep the `.venv3.12/` folder in the project root for easy activation
- **Git:** The `.venv3.12/` folder is typically excluded from git (add to `.gitignore`)
- **Python Version:** Python 3.10+ is supported; 3.12 is recommended for best compatibility
- **Cross-Platform:** Commands work on Windows (PowerShell), Linux, and macOS
- **Hardware:** To use actual Phaser hardware, additional drivers and USB setup may be required
- **Version Naming:** Using `.venv3.12` allows you to maintain separate environments for different Python versions in the same project

---

## Next Steps

1. Activate your virtual environment
2. Install dependencies with `pip install -r requirements.txt`
3. Start Jupyter with `jupyter notebook`
4. Begin with tutorials in the `beam-forming-tutorials/` or `radar-tutorials/` folders

Happy learning! 🚀
