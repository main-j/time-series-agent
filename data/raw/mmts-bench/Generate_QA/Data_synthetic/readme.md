# TS-Foundation Dataset

## 1 Module Introduction

The TS-Foundation dataset is constructed based on a hierarchical progression theory of time series understanding capabilities. The original sequences in the dataset are generated using a modular construction approach. The system first generates three types of fundamental time series units: Trend Sequence Units, Seasonal Sequence Units, and Noise Sequence Units, with flexible parameter control for each unit.

## 2 Directory Structure

```
.
├── meta_info                           # Stores generated time series datasets and features
├── TS_generator                        # Time Series Generator Module
│ ├── noise.py                          # Noise Sequence Unit
│ ├── season.py                         # Seasonal Sequence Unit
│ ├── trend.py                          # Trend Sequence Unit
│ ├── unit.py                           # Waveform parameter settings for randflowvary in season components
│ └── utils.py                          # Time series feature extraction utilities
├── generate_question.py                # Generates Q&A pairs for non-stationary time series datasets and merge all Q&A pairs
├── generate_stationary_question.py     # Generates Q&A pairs for non-stationary time series datasets and merge all Q&A pairs
├── non_stationary.py                   # Generates non-stationary time series and stores their features
├── stationary_synthetic.py             # Generates stationary time series and stores their features
└── index_question_templates.json       # Utility tools and helper functions
```


## 3 Script Usage Guide

### 3.1 Environment Setup
```bash
# Install required dependencies
pip install -r requirements.txt
```
### 3.2 Generate Datasets
```bash
# Generate Stationary Time Series Dataset
python stationary_synthetic.py

# Generate Non-Stationary Time Series Dataset  
python non_stationary_synthetic.py
```
### 3.3 Generate Corresponding Question CSV Files
```bash
# Generate Q&A pairs for Stationary Time Series
python generate_stationary_question.py

# Generate Q&A pairs for Non-Stationary Time Series and final CSV files
python generate_question.py 
```

## 4 Output Files
- Time Series Data: Raw sequence data stored in meta_info/
- Feature Sets: Extracted characteristics JSON files in corresponding dataset
- Question-Answer Pairs: JSON and CSV files containing Q&A for dataset analysis tasks