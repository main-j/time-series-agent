import random
import numpy as np
from .trend import TrendSequenceGenerator
def align_seq(seq):
    """
    Align a sequence's end with its start by adding a linear gradient.
    """
    start_value = seq[0]
    end_value = seq[-1]
    gradient = np.linspace(start_value, end_value, len(seq))
    seq -= gradient
    return seq

class UnitSequenceGenerator:
    """
    A class to generate a UNIT sequence of a given length.
    """
    
    def __init__(self, amplitude=1, length=100, type='amp_unlimited', width_factor=1.0, mutation_level=0.1):
        self.amplitude = amplitude
        self.length = length
        self.type = type
        self.width_factor = width_factor
        self.mutation_level = mutation_level

    def generate(self):
        if self.type == "ecg":
            t = np.arange(self.length)
            # wave params
            params = {
                'p': {'amp': 0.15, 'offset': -10, 'width': 2},
                'q': {'amp': -0.1, 'offset': -3, 'width': 1},
                'r': {'amp': 1.0, 'offset': 0, 'width': 1},
                's': {'amp': -0.2, 'offset': 3, 'width': 1},
                't': {'amp': 0.3, 'offset': 15, 'width': 4}
            }
            
            # mutation process
            for param in params.values():
                param['amp'] *= 1 + random.uniform(-self.mutation_level, self.mutation_level)
                param['offset'] *= 1 + random.uniform(-self.mutation_level, self.mutation_level)
                param['width'] *= 1 + random.uniform(-self.mutation_level, self.mutation_level)
            
            waves = []
            for wave, param in params.items():
                offset = param['offset'] * self.width_factor
                width = param['width'] * self.width_factor
                amp = param['amp'] * self.amplitude
                pos = self.length//2
                waves.append(
                    amp * np.exp(-(t - (pos + offset))**2 / (2 * width**2))
                )
            return sum(waves)
        
        elif self.type == "flowpattern1":
            t = np.arange(self.length)
            length = self.length
            peak1 = random.randint(0, length - max(10, length//10))
            peak2 = random.randint(peak1, length)
            width1 = random.uniform(0.01, self.width_factor) * length
            width2 = random.uniform(0.01, self.width_factor) * length
            wave1 = np.exp(-(t - peak1)**2 / (2 * width1 **2))  # 早高峰
            wave2 = np.exp(-(t - peak2)**2 / (2 * width2 **2))  # 晚高峰
            amp1 = self.amplitude * random.uniform(0.5, 1.5)
            amp2 = self.amplitude * random.uniform(0.5, 1.5)
            t = TrendSequenceGenerator(amplitude=0.0001, delta_s=0.001, length=length, type='amp_limited').generate()

            return align_seq(t + amp1 * wave1 + amp2 * wave2)
        
        elif self.type == "flowpattern2":
            t = np.arange(self.length)
            length = self.length
            peak1 = random.randint(0, length - max(10, length//10))
            width1 = random.uniform(0.01, self.width_factor) * length
            wave1 = np.exp(-(t - peak1)**2 / (2 * width1 **2))  
            amp1 = self.amplitude * random.uniform(0.5, 1.5)
            t = TrendSequenceGenerator(amplitude=0.0001, delta_s=0.0003, length=length, type='amp_limited').generate()

            return align_seq(t + amp1 * wave1)
        
        elif self.type == "flowpattern3":
            t = np.arange(self.length)
            length = self.length
            peak1 = random.randint(length//5, length//2)
            peak2 = random.randint(length//2, length//5*4)
            width1 = random.uniform(0.1*self.width_factor, 0.5*self.width_factor) * length
            width2 = random.uniform(0.1*self.width_factor, 0.5*self.width_factor) * length
            wave1 = np.exp(-(t - peak1)**2 / (2 * width1 **2))  # 早高峰
            wave2 = np.exp(-(t - peak2)**2 / (2 * width2 **2))  # 晚高峰
            amp1 = self.amplitude * random.uniform(0.5, 1.5)
            amp2 = self.amplitude * random.uniform(0.5, 1.5)
            t = TrendSequenceGenerator(amplitude=0.0001, delta_s=0.0005, length=length, type='amp_limited').generate()

            return align_seq(t + amp1 * wave1 + amp2 * wave2)
        
        elif self.type == "flowpattern4":
            length_factor = random.uniform(0.3, 0.7)
            t = np.arange(int(self.length * length_factor))
            length = self.length
            peak1 = random.randint(0, length - max(10, length//10))
            peak2 = random.randint(peak1, length)
            width1 = random.uniform(0.1, self.width_factor) * length
            width2 = random.uniform(0.1, self.width_factor) * length
            wave1 = np.exp(-(t - peak1)**2 / (2 * width1 **2))
            wave2 = np.exp(-(t - peak2)**2 / (2 * width2 **2))
            sig1 = np.zeros(length)
            start = random.randint(0, length - len(wave1))
            sig1[start:start+len(wave1)] = align_seq(wave1- wave1[0])
            sig2 = np.zeros(length)
            sig2[start:start+len(wave2)] = align_seq(wave2- wave2[0])
            amp1 = self.amplitude * random.uniform(0.5, 1.5)
            amp2 = self.amplitude * random.uniform(0.5, 1.5)
            t = TrendSequenceGenerator(amplitude=0.0001, delta_s=0.0001, length=length, type='amp_limited').generate()
            return align_seq(t + amp1 * sig1 + amp2 * sig2)

            




if __name__ == "__main__":
    generator = UnitSequenceGenerator(amplitude=1, length=5000, type='flowpattern1', width_factor=0.1)
    sequence = generator.generate()
    import matplotlib.pyplot as plt
    plt.plot(sequence)
    plt.savefig('flowpattern1.png')