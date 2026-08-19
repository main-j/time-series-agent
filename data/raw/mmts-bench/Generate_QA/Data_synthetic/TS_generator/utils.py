# utils.py
# Define class FeatureExtractor to extract features from the sequence
import numpy as np
from hurst import compute_Hc

class FeatureExtractor:
    def __init__(self, period, seq_t, seq_s, seq_n, ori_feature = {}):
        # note that seq_t&seq_s&seq_n are numpy arrays
        if not isinstance(seq_t, np.ndarray):
            seq_t = np.array(seq_t)
        if not isinstance(seq_s, np.ndarray):
            seq_s = np.array(seq_s)
        if not isinstance(seq_n, np.ndarray):
            seq_n = np.array(seq_n)
        self.period = period
        self.seq_t = seq_t
        self.seq_s = seq_s
        self.seq_n = seq_n
        self.ts = seq_t + seq_s + seq_n
        if ori_feature:
            self.ori_feature = ori_feature
        else:
            self.ori_feature = {}

    def seasonal_strength(self):
        # calculate the seasonal strength of the sequence
        var_s_plus_n = np.var(self.seq_s + self.seq_n)
        var_n = np.var(self.seq_n)
        seasonal_strength = max(0, min(1, 1 - var_n / var_s_plus_n))
        return seasonal_strength
    
    def trend_strength(self):
        # calculate the trend strength of the sequence
        var_t_plus_n = np.var(self.seq_t + self.seq_n)
        var_n = np.var(self.seq_n)
        trend_strength = max(0, min(1, 1 - var_n / var_t_plus_n))
        return trend_strength
    
    def noise_strength(self):
        # calculate the noise strength of the sequence
        var_n = np.var(self.seq_n)
        var_ori = np.var(self.ts)
        noise_strength = max(0, min(1, var_n / var_ori))
        return noise_strength
    
    def cal_slope(self):
        # calculate the slope of the sequence
        slope = (self.ts[-1] - self.ts[0]) / (len(self.ts) - 1)
        return slope    
    
    def coefficient_of_variation(self):
        return np.std(self.ts) / np.abs(np.mean(self.ts))
    
    def simple_returns_std(self):
        simple_returns = np.diff(self.ts) / self.ts[:-1]
        return np.std(simple_returns)
    
    def log_returns_std(self):
        min_ts = min(self.ts)
        if min_ts <= 0:
            shifted_ts = self.ts + np.abs(min_ts) + 1
        else:
            shifted_ts = self.ts
        log_returns = np.diff(np.log(shifted_ts))
        return np.std(log_returns)
    
    def PCT(self, pct):
        sorted_ts = np.sort(self.ts)
        return sorted_ts[int(len(sorted_ts) * pct)]
    
    def hurst(self):
        H, c, data = compute_Hc(self.seq_t + self.seq_s + self.seq_n)
        return H
    
    def extract_features(self):
        features = {}
        features['period'] = self.period
        features['seasonal_strength'] = self.seasonal_strength()
        features['trend_strength'] = self.trend_strength()
        features['noise_strength'] = self.noise_strength()
        features['slope'] = self.cal_slope()
        features['coefficient_of_variation'] = self.coefficient_of_variation()
        features['simple_returns_std'] = self.simple_returns_std()
        features['log_returns_std'] = self.log_returns_std()
        features['hurst'] = self.hurst()
        features['max'] = max(self.ts)
        features['max_point'] = np.argmax(self.ts).tolist()
        features['min'] = min(self.ts)
        features['min_point'] = np.argmin(self.ts).tolist()
        features['mean'] = np.mean(self.ts)
        features['median'] = np.median(self.ts)
        features['std'] = np.std(self.ts)
        features['PCT50'] = self.PCT(0.5)
        features['PCT90'] = self.PCT(0.9)
        features['PCT99'] = self.PCT(0.99)
        features.update(self.ori_feature)
        return features
    