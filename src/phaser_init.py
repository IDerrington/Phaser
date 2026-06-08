"""
Phaser initialization helper to fix common issues with CN0566 setup.

This module provides wrapper functions that handle common initialization problems:
- LTE filter file path resolution
- Hardware detection and connection
- Default configuration
"""

import os
from pathlib import Path
from adi.cn0566 import CN0566

def get_filter_path(filter_name="LTE20_MHz.ftr"):
    """
    Get the full path to an LTE filter file.

    Searches in common locations:
    1. resources/ directory at repo root
    2. Current working directory
    3. pyadi-iio package filters (if available)

    Args:
        filter_name: Name of the filter file (default: "LTE20_MHz.ftr")

    Returns:
        str: Full path to the filter file

    Raises:
        FileNotFoundError: If filter file cannot be found
    """
    # Try repo resources directory
    repo_root = Path(__file__).parent.parent
    filter_path = repo_root / "resources" / filter_name
    if filter_path.exists():
        return str(filter_path)

    # Try current working directory
    cwd_path = Path.cwd() / filter_name
    if cwd_path.exists():
        return str(cwd_path)

    # Try ../resources from CWD (for notebooks in subdirectories)
    rel_path = Path.cwd() / "resources" / filter_name
    if rel_path.exists():
        return str(rel_path)

    # Try ../../resources from CWD
    rel_path2 = Path.cwd().parent / "resources" / filter_name
    if rel_path2.exists():
        return str(rel_path2)

    raise FileNotFoundError(
        f"Could not find {filter_name}. Searched:\n"
        f"  - {filter_path}\n"
        f"  - {cwd_path}\n"
        f"  - {rel_path}\n"
        f"  - {rel_path2}\n"
        "Please ensure the filter file is in the resources/ directory."
    )


def init_phaser_sdr(my_phaser, freq_sample, freq_sdr, rx_gain=-6, tx_gain=-6,
                     buffer_size=1024, filter_name="LTE20_MHz.ftr"):
    """
    Initialize Phaser SDR with automatic filter path resolution.

    This is a drop-in replacement for my_phaser.SDR_init() that automatically
    finds the LTE filter file path.

    Args:
        my_phaser: CN0566 instance
        freq_sample: Sample rate (Hz)
        freq_sdr: SDR center frequency (Hz)
        rx_gain: RX gain (dB), default -6
        tx_gain: TX gain (dB), default -6
        buffer_size: Buffer size in samples, default 1024
        filter_name: LTE filter filename, default "LTE20_MHz.ftr"

    Example:
        >>> from phaser_init import init_phaser_sdr
        >>> my_phaser = CN0566(uri="ip:phaser.local")
        >>> my_phaser.configure(device_mode="rx")
        >>> init_phaser_sdr(my_phaser, 30e6, 1e9, rx_gain=-6, buffer_size=1024)
    """
    # Standard SDR initialization (without filter)
    my_phaser.sdr.sample_rate = int(freq_sample)
    my_phaser.sdr.rx_lo = int(freq_sdr)
    my_phaser.sdr.tx_lo = int(freq_sdr)
    my_phaser.sdr.tx_cyclic_buffer = True
    my_phaser.sdr.tx_hardwaregain_chan0 = int(tx_gain)
    my_phaser.sdr.tx_hardwaregain_chan1 = int(tx_gain)
    my_phaser.sdr.gain_control_mode_chan0 = "manual"
    my_phaser.sdr.gain_control_mode_chan1 = "manual"
    my_phaser.sdr.rx_hardwaregain_chan0 = int(rx_gain)
    my_phaser.sdr.rx_hardwaregain_chan1 = int(rx_gain)

    # Apply filter with correct path
    try:
        filter_path = get_filter_path(filter_name)
        my_phaser.sdr.filter = filter_path
        print(f"Loaded filter: {filter_path}")
    except FileNotFoundError as e:
        print(f"Warning: {e}")
        print("Continuing without filter...")

    # Set buffer size
    my_phaser.sdr.rx_buffer_size = int(buffer_size)


def quick_init(uri="ip:phaser.local", freq_sample=30e6, freq_sdr=10e9,
               rx_gain=-6, mode="rx", buffer_size=1024):
    """
    Quick initialization of CN0566 Phaser with sensible defaults.

    Args:
        uri: Device URI (default: "ip:phaser.local")
        freq_sample: Sample rate in Hz (default: 30 MHz)
        freq_sdr: SDR center frequency in Hz (default: 10 GHz)
        rx_gain: RX gain in dB (default: -6)
        mode: Device mode "rx" or "tx" (default: "rx")
        buffer_size: RX buffer size (default: 1024)

    Returns:
        CN0566: Initialized Phaser instance

    Example:
        >>> from phaser_init import quick_init
        >>> my_phaser = quick_init(freq_sdr=10.3e9)
        >>> data = my_phaser.sdr.rx()
    """
    print(f"Connecting to Phaser at {uri}...")
    my_phaser = CN0566(uri=uri)

    print(f"Configuring for {mode} mode...")
    my_phaser.configure(device_mode=mode)

    print("Initializing SDR...")
    init_phaser_sdr(my_phaser, freq_sample, freq_sdr, rx_gain=rx_gain,
                     buffer_size=buffer_size)

    print(f"✓ Phaser initialized successfully")
    print(f"  Sample Rate: {freq_sample/1e6:.1f} Msps")
    print(f"  Center Freq: {freq_sdr/1e9:.2f} GHz")
    print(f"  RX Gain: {rx_gain} dB")

    return my_phaser


# Convenience function names
init_sdr = init_phaser_sdr  # Alias for backwards compatibility
