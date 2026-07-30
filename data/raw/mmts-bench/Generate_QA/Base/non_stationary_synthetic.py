from TS_generator.season import *
from TS_generator.trend import *
from TS_generator.utils import *
import random
import os
import json
import numpy as np
import matplotlib.pyplot as plt
max_length = 1000
min_length = 128
max_amplitude = 1000
min_amplitude = 0.1
max_delta_s = 0.1
min_delta_s = 0.01

def PCT(ts, pct):
    return np.percentile(ts, pct)

def trend_season_mixed(amp, delta_s, length):
    #generate trend series
    trend_s = TrendSequenceGenerator(amplitude=amp, delta_s=delta_s, length=length).generate()
    trend_s = np.array(trend_s)

    period = length//5
    season_s, period = PeriodicSequenceGenerator(amplitude=amp, period=period, length=length, type=wave).generate()
    season_s = np.array(season_s)

    s_t_ratio = random.uniform(0.1, 0.9)
    cropped_season_s = season_s[:int(length*s_t_ratio)]
    cropped_trend_s = trend_s[int(length*s_t_ratio):]

    #generate non-stationary series
    if random.random() < 0.5:
        non_stationary_s = np.concatenate([cropped_trend_s, cropped_season_s])
    else:
        non_stationary_s = np.concatenate([cropped_season_s, cropped_trend_s])
    return non_stationary_s, s_t_ratio

def different_season_wave_mixed(wave_type, amp, length):
    wave1 = random.choice(wave_type)
    wave2 = random.choice(wave_type)    
    while wave1 == wave2:
        wave2 = random.choice(wave_type)
    period_init = length//5
    season_s1, period = PeriodicSequenceGenerator(amplitude=amp, period=period_init, length=length, type=wave1).generate()
    season_s2, period = PeriodicSequenceGenerator(amplitude=amp, period=period_init, length=length, type=wave2).generate()
    ratio = random.uniform(0.1, 0.9)
    cropped_s1 = season_s1[:int(length*ratio)]
    cropped_s2 = season_s2[int(length*ratio):]

    if random.random() < 0.5:
        non_stationary_s = np.concatenate([cropped_s1, cropped_s2])
    else:
        non_stationary_s = np.concatenate([cropped_s2, cropped_s1])
    return non_stationary_s, ratio

if __name__ == "__main__":
    random.seed(9202)
    wave_type = ['sine', 'square', 'randsine', 'randsquare', 'randseason', 'randseasonq', 'randflow', 'randflowvary']
    cnt = 0
    all_features = []
    print(f'Generating timeseries data...')
    for wave in wave_type:
        for i in range(25):
            #generate trend series
            amp = random.uniform(min_amplitude, max_amplitude)
            delta_s = random.uniform(min_delta_s, max_delta_s)
            length = random.randint(min_length, max_length)
        
            non_stationary_s, s_t_ratio = trend_season_mixed(amp, delta_s, length)
            features = {}
            features['values'] = f'meta_info/non_stationary/values/{cnt}.npy'
            features['wave'] = wave
            features['s_t_ratio'] = s_t_ratio
            features['max'] = max(non_stationary_s)
            features['min'] = min(non_stationary_s)
            features['mean'] = np.mean(non_stationary_s)
            features['std'] = np.std(non_stationary_s)
            features['median'] = np.median(non_stationary_s)
            features['PCT50'] = PCT(non_stationary_s, 50)
            features['PCT90'] = PCT(non_stationary_s, 90)
            features['PCT99'] = PCT(non_stationary_s, 99)
            
            all_features.append(features)

            #save the series
            save_path = f'meta_info/non_stationary/values'
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            np.save(os.path.join(save_path, f'{cnt}.npy'), non_stationary_s)

            if not os.path.exists(f'meta_info/non_stationary/figs'):
                os.makedirs(f'meta_info/non_stationary/figs')
            plt.plot(non_stationary_s)
            plt.savefig(os.path.join(f'meta_info/non_stationary/figs', f'{cnt}.png'))
            plt.close()
            cnt += 1
    
    for i in range(100):
        amp = random.uniform(min_amplitude, max_amplitude)
        length = random.randint(min_length, max_length)
        non_stationary_s, ratio = different_season_wave_mixed(wave_type, amp, length)
        features = {}
        features['values'] = f'meta_info/non_stationary/values/{cnt}.npy'
        features['s_t_ratio'] = ratio
        features['max'] = max(non_stationary_s)
        features['min'] = min(non_stationary_s)
        features['mean'] = np.mean(non_stationary_s)
        features['std'] = np.std(non_stationary_s)
        features['median'] = np.median(non_stationary_s)
        features['PCT50'] = PCT(non_stationary_s, 50)
        features['PCT90'] = PCT(non_stationary_s, 90)
        features['PCT99'] = PCT(non_stationary_s, 99)
        np.save(f'meta_info/non_stationary/values/{cnt}.npy', non_stationary_s)
        plt.plot(non_stationary_s)
        plt.savefig(os.path.join(f'meta_info/non_stationary/figs', f'{cnt}.png'))
        plt.close()
        all_features.append(features)
        cnt += 1

    with open(f'meta_info/non_stationary/all_features.json', 'w') as f:
        json.dump(all_features, f, indent=4)    