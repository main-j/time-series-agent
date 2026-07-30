import math
import random
from .unit import UnitSequenceGenerator
from .trend import TrendSequenceGenerator
import scipy.signal as signal
import numpy as np

def quantize(seq, levels):
    """
    A function to quantize a sequence with a given number of levels.

    args:
        seq: a list of numbers, the sequence to be quantized.
        levels: an int, the number of levels to quantize the sequence.

    returns:
        a list of numbers, the quantized sequence.
    """

    # find the minimum and maximum values in the sequence
    min_val = min(seq)
    max_val = max(seq)

    # calculate the step size for each level
    step = (max_val - min_val) / levels

    # initialize an empty list for the quantized sequence
    quantized_seq = []

    # loop through each value in the sequence
    for val in seq:
        # calculate the level index for this value
        level = int((val - min_val) / step)
        # clip the level index to be within [0, levels - 1]
        level = max(0, min(level, levels - 1))
        # calculate the quantized value for this level
        quantized_val = min_val + level * step
        # append it to the quantized sequence
        quantized_seq.append(quantized_val)

    return quantized_seq


class PeriodicSequenceGenerator:
    """
    A class to generate a periodic sequence with a given amplitude and period.

    args:
        amplitude: float, the amplitude parameter of the sequence. Default is 1.
        period: int, the period parameter of the sequence. Default is 10.
        length: int, the length of the sequence. Default is 100.
        type: string, the type of the sequence. Choose from 'sine', 'square', 'randsine', 'randsquare', 'randseason'. Default is 'sine'.
    """

    def __init__(self, amplitude=1, period=10, length=100, type='sine', wavnum=2, seq=[], delta_s=1, shake_factor=0.01, limit_type='amp_unlimited',levels=5,flex_factor=0,smooth = 0):
        self.amplitude = amplitude
        self.period = period
        self.length = length
        self.type = type
        self.wavnum = wavnum
        self.seq = seq
        self.delta_s = delta_s
        self.shake_factor = shake_factor
        self.limit_type = limit_type
        self.levels = levels
        self.flex_factor = flex_factor 
        self.smooth = smooth 

 
    def generate(self):
        # initialize an empty sequence
        seq = []

        # generate the sequence according to the type
        if self.type == 'sine':
            # generate a sine wave with the given amplitude and period
            phase = random.uniform(0, 2 * math.pi)  
            for i in range(self.length):
                # calculate the angle in radians
                angle = 2 * math.pi * i / self.period + phase
                # calculate the value of the sine wave at this angle
                value = self.amplitude * math.sin(angle)
                # append it to the sequence
                seq.append(value)
            final_period = self.period

        elif self.type == 'square':
            # generate a square wave with the given amplitude and period
            phase_shift = random.uniform(0, self.period)
            for i in range(self.length):
                # calculate the phase of the square wave
                phase = (i + phase_shift) % self.period
                # determine the value of the square wave at this phase
                if phase < self.period / 2:
                    value = self.amplitude # high state
                else:
                    value = -self.amplitude # low state
                # append it to the sequence
                seq.append(value)
            final_period = self.period

        elif self.type == 'triangle':
            # generate a triangle wave with the given amplitude and period
            phase_shift = random.uniform(0, self.period)
            for i in range(self.length):
                # calculate the phase of the triangle wave
                phase = (i + phase_shift) % self.period
                # determine the value of the triangle wave at this phase
                if phase < self.period / 2:
                    value = -self.amplitude + (2 * self.amplitude / (self.period / 2)) * phase # up from -A to +A
                else:
                    value = self.amplitude - (2 * self.amplitude / (self.period / 2)) * (phase - self.period / 2) # down from +A to -A
                # append it to the sequence
                seq.append(value)
            final_period = self.period

        elif self.type == 'sawtooth':
            # generate a sawtooth wave with the given amplitude and period
            phase_shift = random.uniform(0, self.period)
            for i in range(self.length):
                # determine the value of the sawtooth wave at this phase
                phase = (i + phase_shift) % self.period
                value = -self.amplitude + (2 * self.amplitude / self.period) * phase # up from -A to +A
                seq.append(value)
            final_period = self.period

        elif self.type == 'randsine':
            # generate a random sine wave
            amplitude_list = []
            freq_list = []
            for i in range(self.wavnum):
                # generate random amplitude
                amp = random.uniform(0, self.amplitude)
                amplitude_list.append(amp)
                # generate random phase
                phase = random.uniform(0, 2*math.pi)
                # generate random frequency
                freq_limit = 2 * math.pi / self.period
                freq = random.uniform(freq_limit/2, freq_limit)
                if i == 0:
                    freq_list.append(freq_limit)
                else:
                    freq_list.append(freq)

            for i in range(self.length):
                # initialize the value
                value = 0
                for j in range(self.wavnum):
                    angle = i * freq_list[j] + phase
                    value += amplitude_list[j] * math.sin(angle)
                    # append it to the sequence
                seq.append(value)
            final_period = 0
        
        elif self.type == 'randsquare':
            # generate a random square wave
            amplitude_list = []
            period_list = []
            for i in range(self.wavnum):
                # generate random amplitude
                amp = random.uniform(0, self.amplitude)
                amplitude_list.append(amp)
                # generate random period
                period = random.randint(int(self.period/2), self.period)
                if i == 0:
                    period_list.append(self.period)
                else:
                    period_list.append(period)
                # generate random phase
                phase = random.randint(0, period)

            for i in range(self.length):
                # initialize the value
                value = 0
                for j in range(self.wavnum):
                    # calculate the phase of the square wave
                    phase_ = (i +  phase) % period
                    # determine the value of the square wave at this phase
                    if phase_ < period_list[j] / 2:
                        value += amplitude_list[j] # high state
                    else:
                        value += -amplitude_list[j] # low state
                    # append it to the sequence
                    
                seq.append(value)
            final_period = 0

        elif self.type == 'randseason':
            # generate a normal seasonal sequence
            if len(self.seq) > 0:
                # sequence is set by hand
                seq_ = self.seq
                period = self.period
            else:
                # sequence is generated automaticaly
                period = random.randint(int(self.period/2), self.period)
                t = TrendSequenceGenerator(amplitude=self.amplitude, delta_s=self.delta_s, length=period,type=self.limit_type)
                seq_ = t.generate()
                seq_ = np.array(seq_) - np.mean(seq_)
            # generate
            # print(len(seq_))
            phase = random.randint(0, period)
            phase_ = phase
            shake = 1 + random.uniform(-self.shake_factor,self.shake_factor)
            flex = 1 + random.uniform(-self.flex_factor,self.flex_factor)
            num = int(period* flex)
            seq_resampled = signal.resample(seq_, num)
            # romove
            for i in range(self.length):
                # initialize the value
                value = 0
                # calculate the phase of the square wave
                phase_ = (phase_ + 1) % num
                # determine the value of the wave at this phase
                value += seq_resampled[phase_] # high state
                # append it to the sequence
                if phase_ == 0:
                    shake = 1 + random.uniform(-self.shake_factor,self.shake_factor)
                    flex = 1 + random.uniform(-self.flex_factor,self.flex_factor)
                seq.append(value* shake)
            final_period = 0

        elif self.type == 'randseasonq':
            # generate a quantitive seasonal sequence
            if len(self.seq) > 0:
                # sequence is set by hand
                seq_ = self.seq
                period = self.period
            else:
                # sequence is generated automaticaly
                period = random.randint(int(self.period/2), self.period)
                t = TrendSequenceGenerator(amplitude=self.amplitude, delta_s=self.delta_s, length=period,type=self.limit_type)
                seq_ = t.generate()
            # generate
            phase = random.randint(0, period)
            phase_ = phase
            shake = 1 + random.uniform(-self.shake_factor,self.shake_factor)
            flex = 1 + random.uniform(-self.flex_factor,self.flex_factor)
            for i in range(self.length):
                # initialize the value
                value = 0
                num = int(period* flex)
                seq_resampled = signal.resample(seq_, num)
                # calculate the phase of the square wave
                phase_ = (phase_ + 1) % num
                # determine the value of the wave at this phase
                value += seq_resampled[phase_] # high state
                # append it to the sequence
                if phase_ == 0:
                    shake = 1 + random.uniform(-self.shake_factor,self.shake_factor)
                    flex = 1 + random.uniform(-self.flex_factor,self.flex_factor)
                seq.append(value * shake)
            seq = quantize(seq, self.levels)  
            final_period = 0

        elif self.type == 'randflow':
            if len(self.seq) > 0:
                # sequence is set by hand
                seq_ = self.seq
                period = self.period
            else:
                # sequence is generated automaticaly
                flowtype = ['flowpattern1','flowpattern2','flowpattern3']
                period = random.randint(int(self.period/2), self.period)
                rand_type = random.choice(flowtype)
                seq_ = UnitSequenceGenerator(amplitude=self.amplitude, length=self.length,type=rand_type, width_factor=random.uniform(0.3,1)).generate()
            phase = random.randint(0, period)
            phase_ = phase
            shake = 1 + random.uniform(-self.shake_factor,self.shake_factor)
            flex = 1 + random.uniform(-self.flex_factor,self.flex_factor)
            for i in range(self.length):
                # initialize the value
                value = 0
                num = int(period* flex)
                seq_resampled = signal.resample(seq_, num)
                # calculate the phase of the square wave
                phase_ = (phase_ + 1) % num
                # determine the value of the wave at this phase
                value += seq_resampled[phase_] # high state
                # append it to the sequence
                if phase_ == 0:
                    shake = 1 + random.uniform(-self.shake_factor,self.shake_factor)
                    flex = 1 + random.uniform(-self.flex_factor,self.flex_factor)
                ratio = max(phase_ / num , (num - phase_) / num)
                seq.append(value * ratio + value * shake * (1 - ratio))
            final_period = 0

        elif self.type == 'randflowvary':
            if len(self.seq) > 0:
                # sequence is set by hand
                seq_ = self.seq
                period = self.period
            else:
                # sequence is generated automaticaly
                flowtype = ['flowpattern1','flowpattern2','flowpattern3']
                period = random.randint(int(self.period/3), self.period)
                rand_type = random.choice(flowtype)
                seq_ = UnitSequenceGenerator(amplitude=self.amplitude, length=self.length,type=rand_type, width_factor=random.uniform(0.3,1)).generate()
            long_period = random.randint(2,5)
            phase = random.randint(0, period)
            phase_ = phase
            shake = 1 + random.uniform(-self.shake_factor,self.shake_factor)
            flex = 1 + random.uniform(-self.flex_factor,self.flex_factor)
            long_pattern = [random.uniform(-1.5,1.5) for _ in range(long_period)]
            for i in range(self.length):
                # initialize the value
                value = 0
                num = round(period* flex)
                seq_resampled = signal.resample(seq_, num)
                # calculate the phase of the square wave
                phase_ = (phase_ + 1) % num
                
                # determine the value of the wave at this phase
                value += seq_resampled[phase_]
                # append it to the sequence
                if phase_ == 0:
                    shake = long_pattern[(i//period) % long_period] + random.uniform(-self.shake_factor,self.shake_factor)
                    flex = 1 + random.uniform(-self.flex_factor,self.flex_factor)
                ratio = max(phase_ / num , (num - phase_) / num)
                seq.append(value * ratio + value * shake * (1 - ratio))
            final_period = 0
        
        else:
            # invalid type
            raise ValueError("Invalid type.")

        return seq, final_period
    
wave_type_list = {'sine': 0.15, 'square': 0.15, 'triangle': 0.15, 'sawtooth': 0.15, 
                  'randsine': 0.15, 'randsquare': 0.15, 
                  'randflowvary': 0.1}    

if __name__ == "__main__":
    generator = PeriodicSequenceGenerator(amplitude=100, period=500, length=5000, type='randflowvary', shake_factor=0.1, flex_factor=0.1, limit_type='amp_limited')
    sequence_season = generator.generate()
    import matplotlib.pyplot as plt
    plt.plot(sequence_season)
    plt.show()