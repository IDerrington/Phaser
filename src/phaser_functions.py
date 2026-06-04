#!/usr/bin/env python3
#  Must use Python 3
# Copyright (C) 2022 Analog Devices, Inc.
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#     - Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     - Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in
#       the documentation and/or other materials provided with the
#       distribution.
#     - Neither the name of Analog Devices, Inc. nor the names of its
#       contributors may be used to endorse or promote products derived
#       from this software without specific prior written permission.
#     - The use of this software may or may not infringe the patent rights
#       of one or more patent holders.  This license does not release you
#       from the requirement that you obtain separate licenses from these
#       patent holders to use this software.
#     - Use of the software either in source or binary form, must be run
#       on or directly connected to an Analog Devices Inc. component.
#
# THIS SOFTWARE IS PROVIDED BY ANALOG DEVICES "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, NON-INFRINGEMENT, MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED.
#
# IN NO EVENT SHALL ANALOG DEVICES BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, INTELLECTUAL PROPERTY
# RIGHTS, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
# THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


# Utility functions for CN0566 Phaser

import pickle
from time import sleep
import os
import sys
from pathlib import Path

# Add current directory to path to import phaser_init
sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
from numpy import (
    absolute,
    argmax,
    argsort,
    cos,
    exp,
    floor,
    linspace,
    log10,
    multiply,
    pi,
)
from numpy.fft import fft, fftfreq, fftshift
from scipy import signal


def to_sup(angle):
    """ Return suplimentary angle if greater than 180 degrees. """
    if angle > 180.0:
        angle -= 360.0
    return angle


def find_peak_bin(cn0566, verbose=False):
    """ Simple function to find the peak frequency bin of the incoming signal.
        sets nomial phases and gains first."""
    win = np.blackman(cn0566.sdr.rx_buffer_size)
    
    # First, locate fundamental.
    cn0566.set_all_gain(127)
    cn0566.set_beam_phase_diff(0.0)
    data = cn0566.sdr.rx()  # read a buffer of data
    y_sum = (data[0] + data[1]) * win
    s_sum = np.fft.fftshift(np.absolute(np.fft.fft(y_sum)))
    return np.argmax(s_sum)

def Calculate_Steering_Angle(PhDelta, cn0566):
    # Calculate the beam steering angle
    if PhDelta >= 0:
        SteerAngle = np.degrees(
            np.arcsin(
                max(
                    min(
                        1,
                        (cn0566.c * np.radians(np.abs(PhDelta)))
                        / (2 * np.pi * cn0566.signalFreq * cn0566.element_spacing),
                    ),
                    -1,
                )
            )
        )
              # positive PhaseDelta covers 0deg to 90 deg
    else:
        SteerAngle = -(
            np.degrees(
                np.arcsin(
                    max(
                            min(
                                1,
                                (cn0566.c * np.radians(np.abs(PhDelta)))
                                / (
                                    2
                                    * np.pi
                                    * cn0566.signalFreq
                                    * cn0566.element_spacing
                                ),
                            ),
                            -1,
                        )
                    )
                )
            )  # negative phase delta covers 0 deg to -90 deg
    
    return SteerAngle
            
def doa_scan(cn0566):
    """
    Sweep phase difference, collect A-averaged, non-windowed time-domain SUM/DIFF
    for each phase/steering angle. No FFTs, no plots.

    Returns:
      phaseValues : (P,) commanded phase deltas (generated exactly as requested)
      angles_deg  : (P,) steering angle for each phase
      sum_avg     : (P, T) averaged (ch0 + ch1) * window
      diff_avg    : (P, T) averaged (ch0 - ch1) * window
    """
    sweep_angle = 180
    phaseValues = np.arange( -(sweep_angle), (sweep_angle), cn0566.phase_step_size)

    # Array dimensions
    T = int(cn0566.sdr.rx_buffer_size)
    A = int(cn0566.Averages)
    P = phaseValues.size
    
     # Window: unit-mean Blackman (keeps amplitude scale familiar)
    w = np.blackman(T).astype(np.complex64)
    w /= np.average(w)  # unit mean
    
    ch0_avg = np.zeros((P,T) , dtype=np.complex64)
    ch1_avg = np.zeros((P,T), dtype=np.complex64)
    sum_avg  = np.zeros((P, T), dtype=np.complex64)
    diff_avg = np.zeros((P, T), dtype=np.complex64)
    angles_deg = np.empty(P, dtype=float)

    # Iterate through all the phase deltas
    for p, phDelta in enumerate(phaseValues):
        cn0566.set_beam_phase_diff(phDelta)

        acc0 = np.zeros(T, dtype=np.complex64)
        acc1 = np.zeros(T, dtype=np.complex64)

        # Collect A averages of the two channels
        for _ in range(1):
            rx = cn0566.sdr.rx()  # expect two channels of length T
     
            x0 = np.asarray(rx[0], dtype=np.complex64)
            x1 = np.asarray(rx[1], dtype=np.complex64)

            acc0 += x0 *w
            acc1 += x1 *w

        x0_avg = acc0 / A
        x1_avg = acc1 / A

        ch0_avg[p, :] = x0_avg
        ch1_avg[p, :] = x1_avg
        sum_avg[p, :] = x0_avg + x1_avg
        diff_avg[p, :] = x0_avg - x1_avg
        angles_deg[p]  = Calculate_Steering_Angle(phDelta, cn0566)

    return angles_deg, sum_avg, diff_avg, ch0_avg, ch1_avg



def calculate_plot(cn0566, gcal_element=0, cal_element=0):
    """ Calculate all the values required to do different antenna pattern plots.
        parameters:
            cn0566: Handle to CN0566 instance
        returns:
            gain: Antenna gain data
            angle: Antenna angles (calculated from phases sent to array)
            delta: Delta between sub-arrays (for monopulse tracking)
            diff_error:
            xf:
            max_gain:
            PhaseValues: Actual phase values sent to array
    """
    sweep_angle = 180  # This sweeps the beam angle from -70 deg to +70
    
    # These are all the phase deltas (i.e. phase difference between Rx1 and Rx2, then Rx2 and Rx3, etc.) we'll sweep
    PhaseValues = np.arange( -(sweep_angle), (sweep_angle), cn0566.phase_step_size)
    
    gain, delta, angle = (
        [],
        [],
        [],
    )  # Create empty lists
    
    NumSamples = cn0566.sdr.rx_buffer_size
    win = np.blackman(NumSamples)
    win /= np.average(win)
    
    for PhDelta in PhaseValues:  
        # set Phase of channels based on Calibration Flag status and calibration element
        cn0566.set_beam_phase_diff(PhDelta)
         
        total_sum, total_delta = 0, 0
        for count in range(0, cn0566.Averages):  # repeat loop and average the results
            # read a buffer of data from Pluto using pyadi-iio library (adi.py)
            data = (cn0566.sdr.rx())  
            
            # calculate the sum a difference
            data_fft = data[0] + data[1]
            
            y_sum = data_fft * win
            y_delta = (data[0] - data[1]) * win
            
            # take FFT of sum and difference (ingnore phase)
            s_sum = np.fft.fftshift(np.absolute(np.fft.fft(y_sum)))
            s_delta = np.fft.fftshift(np.absolute(np.fft.fft(y_delta)))
            
            s_sum_max_index = np.argmax(s_sum)
              
            s_mag_sum = np.maximum( np.abs( s_sum.max() ) * 2 / np.sum(win), 
                                    10 ** (-15) )          # Prevent taking log of zero
            
            s_mag_delta = np.maximum( np.abs( s_delta[s_sum_max_index] ) * 2 / np.sum(win),
                                     10 ** (-15) )         # Prevent taking log of zero
            
            
             # Convert to dbFs and su,
            total_sum =     total_sum +     ( 20 * np.log10(s_mag_sum / (2 ** 12)) ) 
            total_delta =   total_delta +   ( 20 * np.log10(s_mag_delta / (2 ** 12)))
        # End of for loop
            
        # Calcualte average by dividing sums by loop counts
        PeakValue_sum = total_sum / cn0566.Averages
        PeakValue_delta = total_delta / cn0566.Averages

        # Calculate the steering angle based on the ADAR phase settings.
        SteerAngle = Calculate_Steering_Angle(PhDelta, cn0566)
      
        # Populate the lists
        gain.append(PeakValue_sum)
        delta.append(PeakValue_delta)
        angle.append(SteerAngle)
    
    # Apply window function to data
    y = data_fft * win
    
    # Calculate FFT and shift Nyquist to 0
    sp = np.absolute(np.fft.fft(y))
    sp = np.fft.fftshift(sp)
    
    # Scale FFT by window and *2 since we are using half the FFT spectrum
    s_mag = ( np.abs(sp) * 2 / np.sum(win)    )  
    s_mag = np.maximum(s_mag, 10 ** (-15))
    
    # Pluto is a 12 bit ADC, so use that to convert to dBFS
    max_gain = 20 * np.log10( s_mag / (2 ** 12) )  
    ts = 1 / float(cn0566.sdr.sample_rate)
    xf = np.fft.fftfreq(NumSamples, ts)
    xf = np.fft.fftshift(xf)  # this is the x axis (freq in Hz) for our fft plot
    
    # Return values/ parameter based on Calibration Flag status
    return gain, angle, delta, xf, max_gain, PhaseValues


def get_signal_levels(cn0566, verbose=False):
    """" Measure signal levels. Without a decent signal, all bets are off. """
    peak_bin = find_peak_bin(cn0566)
    #    channel_levels, plot_data = measure_channel_gains(cn0566, peak_bin, verbose=False)
    #    return channel_levels

    channel_levels = []

    if verbose is True:
        print("Peak bin at ", peak_bin, " out of ", cn0566.sdr.rx_buffer_size)
    # gcal_element indicates current element/channel which is being calibrated
    for element in range(0, (cn0566.num_elements)):
        if verbose is True:
            print("Calibrating Element " + str(element))

        gcal_val, spectrum = measure_element_gain(cn0566, element, peak_bin, verbose)
        if verbose is True:
            print("Measured signal level (ADC counts): " + str(gcal_val))
        channel_levels.append(gcal_val)  # make a list of intermediate cal values
    return channel_levels


def channel_calibration(cn0566, verbose=False):
    """" Do this BEFORE gain_calibration.
         Performs calibration between the two ADAR1000 channels. Accounts for all
         sources of mismatch between the two channels: ADAR1000s, mixers, and
         the SDR (Pluto) inputs. """
    peak_bin = find_peak_bin(cn0566)
    channel_levels, plot_data = measure_channel_gains(cn0566, peak_bin, verbose=False)
    ch_mismatch = 20.0 * np.log10(channel_levels[0] / channel_levels[1])
    if verbose is True:
        print("channel mismatch: ", ch_mismatch, " dB")
    if ch_mismatch > 0:  # Channel 0 hihger, boost ch1:
        cn0566.ccal = [0.0, ch_mismatch]
    else:  # Channel 1 higher, boost ch0:
        cn0566.ccal = [-ch_mismatch, 0.0]
    pass


def gain_calibration(cn0566, verbose=False):
    """ 
    Perform the Gain Calibration routine.
    
    Set the gain calibration flag and create an empty gcal list. Looping 
    through all the possibility i.e. setting    gain of one of the channel 
    to max and all other to 0 create a zero-list where number of 0's depend 
    on total channels. Replace only 1 element with max gain at a time. Now set 
    gain values according to above Note.
    
    Returns the spectral plots of each element in a list (plot_data).
    """
    
    cn0566.gain_cal = True      # Gain Calibration Flag
    gcalibrated_values = []     # Intermediate cal values list
    plot_data = []
    
    # Find the index / bin with the peak signal
    peak_bin = find_peak_bin(cn0566)
    
    if verbose is True:
        print("Peak bin at ", peak_bin, " out of ", cn0566.sdr.rx_buffer_size)
    
    """
    Iterate over each element in the array. 
    Measure the FFT of each element and store the values in a list (plot_data).
    Measure the signal level of each element and store the values in a list (gcalibrated_values).
    """
    for gcal_element in range(0, (cn0566.num_elements)):
        if verbose is True:
            print("Calibrating Element " + str(gcal_element))

        """
        gcal is the signal level
        spectrum is the normalised FFT of the received signal
        """
        gcal_val, spectrum = measure_element_gain( cn0566, gcal_element, peak_bin, verbose=True )
        
        if verbose is True:
            print("Measured signal level (ADC counts): " + str(gcal_val))
       
        gcalibrated_values.append(gcal_val)     # make a list of intermediate cal values
        plot_data.append(spectrum)

    """ 
    Minimum gain of intermediated cal val is set to maximum value as we cannot go beyond max value and gain
    of all other channels are set accordingly
    """
    print("gcalibrated values: ", gcalibrated_values)
    
    for k in range(0, 8):
        # x = ((gcalibrated_values[k] * 127) / (min(gcalibrated_values)))
        cn0566.gcal[k] = min(gcalibrated_values) / (gcalibrated_values[k])
    
    # Reset the Gain calibration Flag once system gain is calibrated )
    cn0566.gain_cal = ( False )
    
    # Return the spectral plots of each element
    return plot_data



def measure_channel_gains(cn0566, peak_bin, verbose=False):  # Default to central element
    """
    Calculate all the values required to do different plots. It method calls set_beam_phase_diff and
    sets the Phases of all channel. All the math is done here.
        parameters:
            gcal_element: type=int
                        If gain calibration is taking place, it indicates element number whose gain calibration is
                        is currently taking place
            cal_element: type=int
                        If Phase calibration is taking place, it indicates element number whose phase calibration is
                        is currently taking place
            peak_bin: type=int
                        Peak bin to examine around for amplitude
    """
    
    width = 10  # Bins around fundamental to sum
    win = signal.windows.flattop(cn0566.sdr.rx_buffer_size)
    win /= np.average(np.abs(win))  # Normalize to unity gain
    plot_data = []
    channel_level = []
    
    cn0566.set_rx_hardwaregain(6, False)
    
    # Iterate through the two channels
    for channel in range(0, 2):
        cn0566.set_all_gain(0, apply_cal=False)  # Start with all gains set to zero
        
        # 1-channel because wonky channel mapping!!
        cn0566.set_chan_gain( (1 - channel) * 4 + 0, 127, apply_cal=False ) # Set element to max
        cn0566.set_chan_gain( (1 - channel) * 4 + 1, 127, apply_cal=False ) # Set element to max
        cn0566.set_chan_gain( (1 - channel) * 4 + 2, 127, apply_cal=False ) # Set element to max
        cn0566.set_chan_gain( (1 - channel) * 4 + 3, 127, apply_cal=False ) # Set element to max

        sleep(1.0)  # todo - remove when driver fixed to compensate for ADAR1000 quirk
        
        if verbose:
            print("measuring channel ", channel)
        
        total_sum = 0
        
        spectrum = np.zeros(cn0566.sdr.rx_buffer_size)

        for count in range( 0, cn0566.Averages):    # repeat snip loop and average the results
            data = cn0566.sdr.rx()                  # todo - remove once confirmed no flushing necessary
            data = cn0566.sdr.rx()                  # read a buffer of data
            y_sum = (data[0] + data[1]) * win

            # Take FFT of the data (ignore phase), and shift the zero frequency to the center
            s_sum = np.fft.fftshift(np.absolute(np.fft.fft(y_sum)))
            
            spectrum += s_sum

            # Look for peak value within window around fundamental (reject interferers)
            s_mag_sum = np.max(s_sum[peak_bin - width : peak_bin + width])
            total_sum += s_mag_sum

        spectrum /= cn0566.Averages * cn0566.sdr.rx_buffer_size
        PeakValue_sum = total_sum / (cn0566.Averages * cn0566.sdr.rx_buffer_size)
        plot_data.append(spectrum)
        channel_level.append(PeakValue_sum)

    return channel_level, plot_data


def measure_element_gain( cn0566, cal, peak_bin, verbose=False):  # Default to central element
    """ 
        Calculate all the values required to do different plots. The method calls set_beam_phase_diff and
        sets the Phases of all channel. All the math is done here.
        parameters:
            gcal_element: type=int
                        If gain calibration is taking place, it indicates element number whose gain calibration is
                        is currently taking place
            cal_element: type=int
                        If Phase calibration is taking place, it indicates element number whose phase calibration is
                        is currently taking place
            peak_bin: type=int
                        Peak bin to examine around for amplitude
    """
    
    width = 10                                          # Bins around fundamental to sum
    
    cn0566.set_rx_hardwaregain(6)                       # SDR hardware gain set to 6dB (default). Both Rx Channels
    cn0566.set_all_gain(0, apply_cal=False)             # Start with all ADAR1000 gains set to zero
    cn0566.set_chan_gain(cal, 127, apply_cal=False)     # Set cal element gain to max
    
    sleep(1.0)  # todo - remove when driver fixed to compensate for ADAR1000 quirk
    
    if verbose:
        print("measuring element: ", cal)
    
    total_sum = 0
    
    # win = np.blackman(cn0566.sdr.rx_buffer_size)
    win = signal.windows.flattop(cn0566.sdr.rx_buffer_size)
    win /= np.average(np.abs(win))  # Normalize to unity gain
    
    spectrum = np.zeros(cn0566.sdr.rx_buffer_size)

    for count in range(0, cn0566.Averages):  # repeatsnip loop and average the results
        _ = cn0566.sdr.rx()  # todo - remove once confirmed no flushing necessary
        data = cn0566.sdr.rx()  # read a buffer of data
        y_sum = (data[0] + data[1]) * win

        s_sum = np.fft.fftshift(np.absolute(np.fft.fft(y_sum)))
        spectrum += s_sum

        # Look for peak value within window around fundamental (reject interferers)
        s_mag_sum = np.max(s_sum[peak_bin - width : peak_bin + width])
        total_sum += s_mag_sum

    # spectrum` is the average of all the FFTs, normalized by the number of averages and buffer size
    spectrum /= cn0566.Averages * cn0566.sdr.rx_buffer_size
    peakValue_sum = total_sum / (cn0566.Averages * cn0566.sdr.rx_buffer_size)

    return peakValue_sum, spectrum

def phase_cal_sweep(cn0566, peak_bin, ref=0, cal=1):
    """ 
        Calculate all the values required to do different plots. It method
        calls set_beam_phase_diff and sets the Phases of all channel.
        parameters:
            gcal_element: type=int
                        If gain calibration is taking place, it indicates element number whose gain calibration is
                        is currently taking place
            cal_element: type=int
                        If Phase calibration is taking place, it indicates element number whose phase calibration is
                        is currently taking place
            peak_bin: type=int
                        Which bin the fundamental is in.
                        This prevents detecting other spurs when deep in a null.
    """

    cn0566.set_all_gain(0)                          # Reset all ADAD1000 elements to zero gain
    cn0566.set_chan_gain(ref, 127, apply_cal=True)  # Reference element (ADAR) gain set to max  
    cn0566.set_chan_gain(cal, 127, apply_cal=True)  # Calibration element (ADAR) gain set to max
    
    sleep(1.0)

    cn0566.set_chan_phase(ref, 0.0, apply_cal=False)            # Reference element phase to 0

    win = signal.windows.flattop(cn0566.sdr.rx_buffer_size)     # Super important!
    win /= np.average(np.abs(win))                              # Normalize to unity gain
    
    width = 10  # Bins around fundamental to sum
    sweep_angle = 180
    # These are all the phase deltas (i.e. phase difference between Rx1 and Rx2, then Rx2 and Rx3, etc.) we'll sweep
    phaseValues = np.arange(-(sweep_angle), (sweep_angle), cn0566.phase_step_size)

    gain = []  # Create empty lists
    for phase in phaseValues:  # These sweeps phase value from -180 to 180
        # set Phase of channels based on Calibration Flag status and calibration element
        cn0566.set_chan_phase(cal, phase, apply_cal=False)
        total_sum = 0
        for count in range(0, cn0566.Averages):  # repeat loop and average the results
            _ = cn0566.sdr.rx()  # read a buffer of data
            data = cn0566.sdr.rx()
            
            y_sum = (data[0] + data[1]) * win
            s_sum = np.fft.fftshift(np.absolute(np.fft.fft(y_sum)))

            # Apparently the correct way, use flat-top window, look for peak
            s_mag_sum = np.max(s_sum[peak_bin - width : peak_bin + width])      # ?
            s_mag_sum = np.max(s_sum)                                           # ?
            total_sum += s_mag_sum
        
        
        peakValue_sum = total_sum / (cn0566.Averages * cn0566.sdr.rx_buffer_size)
        gain.append(peakValue_sum)

    return ( phaseValues, gain, )  # beam_phase, max_gain


def phase_calibration(cn0566, verbose=False):
    """ 
    Perform the Phase Calibration routine.

    Set the phase calibration flag and create an empty pcal list. Looping through all the possibility
    i.e. setting gain of two adjacent channels to gain calibrated values and all other to 0 create a zero-list
    where number of 0's depend on total channels. Replace gain value of 2 adjacent channel.
    Now set gain values according to above Note.
    """
    peak_bin = find_peak_bin(cn0566)
    if verbose is True:
        print("Peak bin at ", peak_bin, " out of ", cn0566.sdr.rx_buffer_size)

    cn0566.pcal = [0, 0, 0, 0, 0, 0, 0, 0]
    cn0566.ph_deltas = [0, 0, 0, 0, 0, 0, 0]
    plot_data = []
    
    """
    cal_element indicates current element/channel which is being calibrated
    As there are 8 channels and we take two adjacent chans for calibration we have 7 cal_elements
    """
    for cal_element in range(0, 7):
        if verbose is True:
            print("Calibrating Element " + str(cal_element))

        phaseValues, gain, = phase_cal_sweep( cn0566, peak_bin, cal_element, cal_element + 1 ) 

        ph_delta = to_sup((180 - phaseValues[gain.index(min(gain))]) % 360.0)
        
        if verbose is True:
            print("Null found at ", phaseValues[gain.index(min(gain))])
            print("Phase Delta to correct: ", ph_delta)
        
        cn0566.ph_deltas[cal_element] = ph_delta
        cn0566.pcal[cal_element + 1] = to_sup( (cn0566.pcal[cal_element] - ph_delta) % 360.0)
        
        plot_data.append(gain)
    
    return phaseValues, plot_data


def save_hb100_cal(freq, filename="hb100_freq_val.pkl"):
    """ Saves measured frequency calibration file."""
    with open(filename, "wb") as file1:
        pickle.dump(freq, file1)  # save calibrated gain value to a file
        file1.close()


def load_hb100_cal(filename="hb100_freq_val.pkl"):
    """ Load frequency measurement value, set to 10.5GHz if no
        parameters:
            filename: type=string
                      Provide path of gain calibration file
    """
    try:
        with open(filename, "rb") as file1:
            freq = pickle.load(file1)  # Load gain cal values
    except Exception:
        print("file not found, loading default 10.5GHz")
        freq = 10.5e9  # Default frequency
    return freq


def spec_est(x, fs, ref=2 ** 15, plot=False):
    """_summary_

    Args:
        x (_type_): signal to be analyzed
        fs (_type_): sampling frequency
        ref (_type_, optional): No of bits per sample. Defaults to 2**15.
        plot (bool, optional): Plot spectrum. Defaults to False.

    Returns:
        _type_: frequency bins and amplitude
    """
    N = len(x)

    # Apply window
    window = signal.windows.kaiser(N, beta=38)
    window /= np.average(window)
    x = multiply(x, window)

    # Use FFT to get the amplitude of the spectrum
    ampl = 1 / N * fftshift(absolute(fft(x)))
    ampl = 20 * log10(ampl / ref + 10 ** -20)

    # FFT frequency bins
    freqs = fftshift(fftfreq(N, 1 / fs))

    # ampl and freqs for real data
    if not np.iscomplexobj(x):
        ampl = ampl[0 : len(ampl) // 2]
        freqs = freqs[0 : len(freqs) // 2]

    if plot:
        # Plot signal, showing how endpoints wrap from one chunk to the next
        import matplotlib.pyplot as plt

        plt.subplot(2, 1, 1)
        plt.plot(x, ".-")
        plt.plot(1, 1, "r.")  # first sample of next chunk
        plt.margins(0.1, 0.1)
        plt.xlabel("Time [s]")
        # Plot shifted data on a shifted axis
        plt.subplot(2, 1, 2)
        plt.plot((freqs), (ampl))
        plt.margins(0.1, 0.1)
        plt.xlabel("Frequency [Hz]")
        plt.tight_layout()
        plt.show()

    return ampl, freqs


from pathlib import Path
from adi import ad9361
from adi.cn0566 import CN0566
import config_custom as config
import sys

def get_phaser_root():
    """
    Finds the project root by looking for characteristic folder structure.
    The project root should contain both 'resources' and 'src' folders.
    Works regardless of the top-level folder name.
    """
    try:
        # .py script
        current_path = Path(__file__).resolve()
    except NameError:
        # Jupyter notebook
        current_path = Path().resolve()

    # Walk up the directory tree looking for project root
    # Project root should have both 'resources' and 'src' folders
    for parent in [current_path] + list(current_path.parents):
        has_resources = (parent / "resources").exists() and (parent / "resources").is_dir()
        has_src = (parent / "src").exists() and (parent / "src").is_dir()
        
        if has_resources and has_src:
            return parent.resolve()

    raise RuntimeError(
        f"Could not locate project root (with both 'resources' and 'src' folders) from path: {current_path}\n"
        "Make sure you're running from within the project hierarchy."
    )

def set_up_phaser():
    """ Set up the Phaser system. """
    # Initialize the Phaser system here
    # This function can be expanded to include additional setup steps if needed
 
    phaser_root = get_phaser_root()
    resource_path = phaser_root / "resources"

    print(f"Resource path: {resource_path}")

    try:
        print(f"Attempting to connect to R_Pi via ip:{config.RASP_IP_ADDRS}...")
        my_phaser = CN0566(uri="ip:" + config.RASP_IP_ADDRS)
        print(f"CN0566 Connected.")

    except:
        raise Exception("Failed to connect to CN0566. Make sure it is connected and powered on.")

    try:
        print(f"Attempting to connect to Pluto via ip:{config.PLUTO_IP_ADDRS}...")
        my_sdr = ad9361(uri="ip:" + config.PLUTO_IP_ADDRS)
        print(f"PlutoSDR connected.\n")
    except:
        raise Exception("Failed to connect to pluto. Make sure it is connected and powered on.")

    my_phaser.sdr = my_sdr  # Set my_phaser.sdr

    """
     Initialise Pluto
    """
    from phaser_init import init_phaser_sdr

    print(f"Initialise Pluto")
    # By default device_mode is "rx"
    my_phaser.configure(device_mode="rx")
    init_phaser_sdr(my_phaser, 30000000, config.rx_freq, rx_gain=6, tx_gain=-6, buffer_size=1024)

    print(f"Converter Sample Rate = {30000000/1e6} Msps")
    print(f"SDR Tx frequency = {config.tx_freq/1e9} GHz (Not used)")
    print(f"SDR Rx frequency = {config.rx_freq/1e9} GHz (Pluto Rx LO)")
    print(f"Tx Gain = -6")
    print(f"Rx Gain =  6")
    print(f"Buffer size = 1024 bytes \n")

    # Load the gain calibration for pluto. Corrects for Rx 0 / 1 differences
    my_phaser.load_channel_cal(filename=resource_path / "channel_cal_val.pkl")

    # Apply gain calibration
    print(f"Apply channel calibration")
    my_phaser.sdr.rx_hardwaregain_chan0 = (my_phaser.sdr.rx_hardwaregain_chan0 + my_phaser.ccal[0])
    my_phaser.sdr.rx_hardwaregain_chan1 = (my_phaser.sdr.rx_hardwaregain_chan1 + my_phaser.ccal[1])

    print(f"Rx Chan 0 Cal = {my_phaser.ccal[0]}")
    print(f"Rx Chan 1 Cal = {my_phaser.ccal[1]}")

    """
    Set up receive frequency. When using HB100, you need to know its frequency
    fairly accurately. Use the cn0566_find_hb100.py script to measure its frequency
    and write out to the cal file. IF using the onboard TX generator, delete
    the cal file and set frequency via config.py or config_custom.py.
    """
    try:
        my_phaser.signalFreq = load_hb100_cal(filename=resource_path / "hb100_freq_val.pkl")
        print(f"Found signal freq file f = {my_phaser.signalFreq} Hz ",)
    except:
        my_phaser.signalFreq = config.signalFreq
        print(f"No signal freq found, keeping at {my_phaser.signalFreq} ")


    #  Configure SDR parameters.
    # Filter already set by init_phaser_sdr
    # my_sdr.filter = resource_path / "LTE20_MHz.ftr"  # Load LTE 20 MHz filter

    # To disable tx, set attenuation to a high value and set frequency far from rx.
    my_sdr.tx_hardwaregain_chan0 = int(-88)  # this is a negative number between 0 and -88
    my_sdr.tx_hardwaregain_chan1 = int(-88)
    my_sdr.tx_lo = int(1.0e9)


    """
    Configure PLL
    """
    my_phaser.frequency = (int(my_phaser.signalFreq) + config.rx_freq ) // 4  # PLL feedback via /4 VCO output
    my_phaser.freq_dev_step = 5690
    my_phaser.freq_dev_range = 0
    my_phaser.freq_dev_time = 0
    my_phaser.powerdown = 0
    my_phaser.ramp_mode = "disabled"

    print(f"PLL fixed frequency = {my_phaser.frequency}/1e9 GHz")

    """
    If you want to use previously calibrated values load_gain and load_phase values by passing path of previously
    stored values. If this is not done system will be working as uncalibrated system.
    These will fail gracefully and default to no calibration if files not present.
    """

    my_phaser.load_gain_cal(filename= resource_path / "gain_cal_val.pkl")
    my_phaser.load_phase_cal(filename= resource_path / "phase_cal_val.pkl")

    print(f"Gain Cal = {my_phaser.gcal}")
    print(f"Phase Cal = {my_phaser.pcal}")

    """
     To set gain of all channels with different values.
         Here's where you would apply a window / taper function,
         but we're starting with rectangular / SINC1.
    """
    gain_list = [127, 127, 127, 127, 127, 127, 127, 127]
    for i in range(0, len(gain_list)):
        my_phaser.set_chan_gain(i, gain_list[i], apply_cal=True)

    # Averages decide number of time samples are taken to plot and/or calibrate system. By default it is 1.
    my_phaser.Averages = 4

    # Aim the beam at boresight by default
    my_phaser.set_beam_phase_diff(0.0)

    return my_phaser