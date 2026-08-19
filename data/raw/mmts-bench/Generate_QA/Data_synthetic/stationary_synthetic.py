from TS_generator.trend import *
from TS_generator.season import *
from TS_generator.noise import *
from TS_generator.utils import *
from collections import OrderedDict
import os
import json
import random
import matplotlib.pyplot as plt
# synthetic data generator

# define the super parameters
max_length = 2048
min_length = 128
max_amplitude = 1000
min_amplitude = 0.1
max_delta_s = 0.1
min_delta_s = 0.01
random.seed(9212)

qa_num = 500  # 可以适当增加样本数量，因为现在只有一种类型

wave_type_list = {'sine': 0.2, 'square': 0.2, 'triangle': 0.2, 'sawtooth': 0.2, 
                  'randsine': 0.05, 'randsquare': 0.05, 
                  'randflowvary': 0.1}    
noise_type_list = {'uniform': 0.25, 'gauss': 0.25, 'random_walk': 0.25, 'quantization': 0.25}
all_features = [] 
cnt = 0
print(f'Generating timeseries data...')

for wave_type, prob in wave_type_list.items():
    for i in range(int(qa_num * prob)):
        if i < qa_num * prob * 0.25:
            noise_type = 'uniform'
        elif i < qa_num * prob * 0.5:
            noise_type = 'gauss'
        elif i < qa_num * prob * 0.75:
            noise_type = 'random_walk'  
        else:
            noise_type = 'quantization'

        # generate amp, length, delta_s
        amp = random.uniform(min_amplitude, max_amplitude)
        length = random.randint(min_length, max_length)
        delta_s = random.uniform(min_delta_s, max_delta_s)
        features = OrderedDict()
        features['ts_id'] = cnt
        
        # Generate 3 sequences
        trend_seq = TrendSequenceGenerator(amplitude=amp, delta_s=delta_s, length=length).generate()
        trend_seq = np.array(trend_seq)
        
        season_seq, period = PeriodicSequenceGenerator(amplitude=amp, period=length//5, length=length, 
                                                type=wave_type, shake_factor=0.1, flex_factor=0.1).generate()
        season_seq = np.array(season_seq)
        
        noise_amp = amp * random.uniform(0.05, 0.2)  # noise amplitude is 5% to 20% of the main amplitude
        noise_seq = NoiseSequenceGenerator(amplitude=noise_amp, length=length, type=noise_type).generate()
        noise_seq = np.array(noise_seq)
        
        # Use Dirichlet distribution generating 3 sets of weights
        weights = np.random.dirichlet(alpha=[1, 1, 1])
        trend_w, season_w, noise_w = weights
        
        # Combine sequence
        combined_seq = trend_w * trend_seq + season_w * season_seq + noise_w * noise_seq
        
        # features
        feature_extractor = FeatureExtractor(period=period, seq_t=trend_w*trend_seq, seq_s=season_w*season_seq, seq_n=noise_w*noise_seq)
        features.update(feature_extractor.extract_features())
        features['values'] = f'meta_info/stationary/values/{cnt}.npy'
        features['wave_type'] = wave_type
        features['noise_type'] = noise_type
        all_features.append(features)
        
        # save data and fig
        if not os.path.exists(f'meta_info/stationary/values'):
            os.makedirs(f'meta_info/stationary/values')
        np.save(f'meta_info/stationary/values/{cnt}.npy', combined_seq)

        if not os.path.exists(f'meta_info/stationary/figs'):
            os.makedirs(f'meta_info/stationary/figs')
        plt.plot(combined_seq)
        plt.savefig(f'meta_info/stationary/figs/{cnt}.png')
        plt.close()

        cnt += 1
                    
# save all features
with open('meta_info/stationary/all_features.json', 'w') as f:
    json.dump(all_features, f, indent=4)

