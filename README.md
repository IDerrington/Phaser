# CN0566 Phaser - Beamforming and Radar Tutorials

Educational notebooks for learning phased array beamforming and FMCW radar using the Analog Devices CN0566 (Phaser) platform.

## Overview

This repository contains interactive Jupyter notebooks that teach the fundamentals of:
- **Phased array beamforming** - Electronic beam steering, array factors, tapering
- **FMCW radar** - Chirp generation, range-Doppler processing, target detection
- **CN0566 hardware** - ADAR1000, AD9361, ADF4159 programming and calibration

Developed by **Iain Derrington**, FAE and Platforms Engineer at Analog Devices (ADEF Group).

---

## Repository Structure

```
Phaser/
├── beam-forming-tutorials/     # Phased array beamforming fundamentals
│   ├── 1-phaser-basics.ipynb
│   ├── 2-phaser-hardware.ipynb
│   ├── 3-phaser-programming.ipynb
│   ├── 4-phaser-cal.ipynb
│   ├── 5-phaser-steering.ipynb
│   ├── 6-monopulse.ipynb
│   ├── 7-adaptive-bf.ipynb
│   └── resources/
├── radar-tutorials/            # FMCW radar implementation
│   ├── 1-fmcw-basics.ipynb
│   ├── 2-fmcw-basics-implementation.ipynb
│   ├── 3-fmcw-tdd-range-measurement.ipynb
│   ├── 4-fmcw-range-doppler.ipynb
│   ├── 5-fmcw-target-detection.ipynb
│   ├── 6-fmcw-beamforming-integration.ipynb
│   ├── 7-weather-radar.ipynb
│   └── resources/
├── phaser-setup/               # Hardware setup and configuration
│   └── cn0566-setup.ipynb
├── resources/                  # Shared resources (logos, images)
├── requirements.txt            # Python dependencies
└── SETUP.md                    # Installation instructions
```

---

## Getting Started

### 1. Prerequisites

- **Python 3.12+** (recommended)
- **CN0566 Phaser hardware** (for hardware exercises)
- **Jupyter Lab or Jupyter Notebook**
- Git with LFS enabled (for media files)

### 2. Installation

```bash
# Clone the repository with Git LFS
git clone <repository-url>
cd Phaser

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure git for Jupyter notebooks (strips outputs on commit)
nbstripout --install

# Enable Jupyter Lab extensions (for interactive widgets)
jupyter labextension install @jupyter-widgets/jupyterlab-manager
```

**Important:** 
- The notebooks use `%matplotlib widget` for interactive plots, which requires the `ipympl` package (already in requirements.txt). You may need to restart your Jupyter server after installation.
- The `nbstripout --install` command configures git to automatically remove notebook outputs and metadata when committing, keeping the repository clean and preventing merge conflicts.

### 3. Launch Jupyter

```bash
jupyter lab
```

Then navigate to `beam-forming-tutorials/1-phaser-basics.ipynb` to start.

---

## Tutorial Paths

### Path 1: Beamforming Fundamentals (No Hardware Required)

Start here if you want to learn phased array theory using interactive Python simulations:

1. **[1-phaser-basics.ipynb](beam-forming-tutorials/1-phaser-basics.ipynb)** - Array factors, steering angles, tapering
2. **[2-phaser-hardware.ipynb](beam-forming-tutorials/2-phaser-hardware.ipynb)** - CN0566 architecture, signal flow
3. **[6-monopulse.ipynb](beam-forming-tutorials/6-monopulse.ipynb)** - Angle estimation techniques
4. **[7-adaptive-bf.ipynb](beam-forming-tutorials/7-adaptive-bf.ipynb)** - Adaptive beamforming algorithms

### Path 2: FMCW Radar Theory (No Hardware Required)

Learn frequency-modulated continuous-wave radar fundamentals:

1. **[1-fmcw-basics.ipynb](radar-tutorials/1-fmcw-basics.ipynb)** - Chirp signals, beat frequency, range equation
2. **[2-fmcw-basics-implementation.ipynb](radar-tutorials/2-fmcw-basics-implementation.ipynb)** - Software simulation
3. **[4-fmcw-range-doppler.ipynb](radar-tutorials/4-fmcw-range-doppler.ipynb)** - 2D processing
4. **[5-fmcw-target-detection.ipynb](radar-tutorials/5-fmcw-target-detection.ipynb)** - CFAR detection

### Path 3: Hardware Bring-Up (CN0566 Required)

Hardware configuration and calibration:

1. **[cn0566-setup.ipynb](phaser-setup/cn0566-setup.ipynb)** - Initial setup and connectivity
2. **[3-phaser-programming.ipynb](beam-forming-tutorials/3-phaser-programming.ipynb)** - Programming ADAR1000/AD9361
3. **[4-phaser-cal.ipynb](beam-forming-tutorials/4-phaser-cal.ipynb)** - Calibration procedures
4. **[5-phaser-steering.ipynb](beam-forming-tutorials/5-phaser-steering.ipynb)** - Live beam steering

### Path 4: Complete Radar System (CN0566 Required)

Integration of beamforming and radar:

1. **[3-fmcw-tdd-range-measurement.ipynb](radar-tutorials/3-fmcw-tdd-range-measurement.ipynb)** - Range measurement
2. **[6-fmcw-beamforming-integration.ipynb](radar-tutorials/6-fmcw-beamforming-integration.ipynb)** - Beamforming + radar
3. **[7-weather-radar.ipynb](radar-tutorials/7-weather-radar.ipynb)** - Application example

---

## Key Concepts Covered

### Beamforming
- Electronic beam steering via phase shifts
- Array factor and pattern multiplication
- Grating lobes and spatial sampling
- Tapering/windowing for sidelobe control
- Performance metrics: HPBW, SLL, directivity
- Monopulse angle estimation
- Adaptive beamforming (LMS, RLS)

### FMCW Radar
- Chirp generation and beat frequency
- Range-Doppler processing (2D FFT)
- CFAR target detection
- TDD timing and frame structure
- Integration with phased arrays
- Practical implementations

### Hardware (CN0566)
- ADAR1000 beamformer (8-channel, 10 GHz)
- AD9361 transceiver (RF frontend)
- ADF4159 chirp synthesizer
- Raspberry Pi control interface
- libiio and pyadi-iio Python APIs

---

## Hardware Requirements

### For Full Functionality:
- **CN0566 Phaser Board** - Hybrid phased array module
- **ADALM-PLUTO (PlutoSDR)** - Integrated with CN0566
- **Raspberry Pi 4** (optional) - Can control Phaser directly
- **Host PC** - Windows/Linux with USB connection
- **Targets for Testing** - Corner reflectors, metal objects

### Optional:
- Spectrum analyzer
- Signal generator
- Anechoic chamber (for precise measurements)

---

## Dependencies

Core packages (see [requirements.txt](requirements.txt)):
- `numpy`, `scipy`, `matplotlib` - Scientific computing
- `ipywidgets`, `ipympl` - Interactive Jupyter widgets
- `pyadi-iio` - ADI hardware control library
- `libiio` - IIO communication layer
- `nbstripout`, `nbdime` - Git integration for notebooks (automatic output stripping, better diffs)

---

## Troubleshooting

### `%matplotlib widget` Error
If you see `RuntimeError: 'widget' is not a recognised GUI loop or backend name`:

```bash
pip install ipympl
jupyter labextension install @jupyter-widgets/jupyterlab-manager
# Restart Jupyter server
```

### `FileNotFoundError: LTE20_MHz.ftr`
The LTE filter files are in `resources/` directory. Use the helper module instead of `SDR_init()`:

```python
import sys
sys.path.insert(0, '../src')
from phaser_init import init_phaser_sdr

# Replace: my_phaser.SDR_init(freq_sample, 1e9, freq_sdr, 6, -6, 1024)
# With:
init_phaser_sdr(my_phaser, freq_sample, freq_sdr, rx_gain=-6, buffer_size=1024)
```

See [FILTER_FIX.md](FILTER_FIX.md) for detailed solutions.

### `ModuleNotFoundError: No module named 'phaser_functions'`
The `phaser_functions` module is in the `src/` directory. Add this code cell **before** the import in affected notebooks:

```python
import sys
sys.path.insert(0, '../src')
```

See [IMPORT_FIX.md](IMPORT_FIX.md) for detailed solutions and list of affected notebooks.

### Missing Images/Logo
The ADI logo should be in `resources/ADI-Logo-RGB-FullColor.png` at the repository root. If missing, download from [Analog Devices Press Kit](https://www.analog.com/en/about-adi/news-room/press-kits.html).

### Hardware Not Detected
Check `pyadi-iio` and `libiio` installation:
```bash
python -c "import iio; print(iio.version)"
iio_info -s  # Should list network devices
```

### Git LFS Files Not Downloaded
Large media files (videos, animations) require Git LFS:
```bash
git lfs install
git lfs pull
```

### Viewing Notebook Diffs
To see rich visual diffs of notebooks (instead of raw JSON), use `nbdime`:
```bash
# View diff of a notebook
nbdiff notebook.ipynb

# View diff in a web browser
nbdiff-web notebook.ipynb

# Configure git to use nbdime for all notebook diffs
nbdime config-git --enable --global
```

---

## Resources

- **CN0566 Product Page**: https://www.analog.com/cn0566
- **CN0566 Wiki**: https://wiki.analog.com/resources/eval/user-guides/circuits-from-the-lab/cn0566
- **PyADI-IIO Documentation**: https://analogdevicesinc.github.io/pyadi-iio/
- **Jon Kraft's YouTube Channel**: https://www.youtube.com/@jonkraft (Phaser tutorials)

---

## Contact

**Iain Derrington**  
Field Applications & Platform Engineer, ADEF Group  
Analog Devices, Inc.  
Email: Iain.Derrington@analog.com  
LinkedIn: https://www.linkedin.com/in/iderrington

**Jan Hansford**  
Email: Jan.Hansford@analog.com

---

## License

[Add license information here]

---

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request with clear description of changes

---

## Acknowledgments

- Analog Devices ADEF Group
- PyADI-IIO development team
- Open-source contributors
