# MMTS-BENCH: A Comprehensive Benchmark for Evaluating Large Language Models on Time Series Understanding

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/release/python-380/)

## Overview

**MMTS-BENCH** is a comprehensive benchmark designed to evaluate the time series understanding capabilities of Large Language Models (LLMs).  
This repository provides a complete framework for generating question–answer pairs, conducting evaluations, and performing ablation studies on various time-series-related tasks.

The benchmark encompasses multiple evaluation dimensions including **pattern matching**, **temporal reasoning**, and **multimodal time series analysis**, making it a valuable resource for researchers working on time series understanding with LLMs.

## Key Features

- **Comprehensive Evaluation**: Multi-dimensional assessment of time series understanding capabilities  
- **Multiple Task Types**: Pattern matching, temporal reasoning, alignment tasks, and more  
- **Model Agnostic**: Support for both open-source and closed-source LLMs  
- **Automated Generation**: Scripts for generating diverse question–answer pairs  
- **Ablation Studies**: Tools for systematic component analysis  
- **Interactive Visualization**: Gradio-based explorer for intuitive visualization of benchmark data and QA content

---

## Folder Structure

- **Ablation/**: Contains code for model ablation experiments based on the ChatTS model.  
- **Benchmark/**: Contains all sub-datasets of MMTS-Bench stored as `.csv` files.  
- **Generate_QA/**: Contains scripts for generating the sub-datasets of MMTS-Bench.  
- **Run_Test/**: Includes testing scripts for evaluating MMTS-Bench on different models, including **open-source models**, **closed-source models**, and **Time Series Adapted LLMs (TS-LLMs)**.

---

## Interactive Visualization

We provide an interactive web-based explorer to help you visualize and explore the MMTS-BENCH dataset more intuitively:

🌐 **[MMTS-BENCH Explorer](https://huggingface.co/spaces/MMTS-Bench/MMTS-Bench-Explorer)**

This visualization tool allows you to:
- Browse time series data across different domains and task types
- Explore question-answer pairs with interactive charts
- Filter and search through the benchmark dataset
- Understand the distribution and characteristics of the benchmark

---

## Benchmark Dataset Description

Each `.csv` file in the `Benchmark` folder typically includes the following columns:

| Column Name     | Description |
|-----------------|--------------|
| **num**         | Data index |
| **qa_type**     | Type of question |
| **local_overall** | Indicates whether the question is local or global |
| **task_type**   | Task type |
| **question**    | Question text |
| **option**      | Provided options |
| **answer**      | Ground truth answer |
| **domain**      | Domain or source field of the time series data |
| **freq**        | Sampling frequency of the time series |
| **is_univariate** | Whether the time series is univariate |
| **value**       | List of lists representing the time series values |

---

## Environment Setup

The `requirements.txt` file provides a reference environment configuration for successfully running all experiments.  
You can install the necessary dependencies with the following command:

```bash
pip install -r requirements.txt
```
