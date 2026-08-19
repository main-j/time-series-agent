# ChatTS Ablation Experiment Code

This repository contains the key scripts and code for running ablation experiments on **ChatTS**. It is organized into three subfolders:

- **`ChatTS-Components`**: Contains essential `.py` scripts and configuration files for converting the Qwen2.5 series models into ChatTS models.  
- **`LLaMA-Factory-Components`**: The official ChatTS training scripts are adapted from LLaMA Factory. This folder includes the modified scripts tailored for ablation experiments.  
- **`Test-Scripts`**: Includes `eval_model.py` and `cal_acc.py`, which are used for evaluating the trained model and computing accuracy metrics, respectively.  

---

## How to Run the Experiments

**Step 1.** Clone the [ChatTS official training repository](https://github.com/xiezhe-24/ChatTS-Training) locally, and replace the corresponding files with those in the **`LLaMA-Factory-Components`** folder.  

**Step 2.** Download the [ChatTS official training dataset](https://huggingface.co/datasets/ChatTSRepo/ChatTS-Training-Dataset). Following the recommended strategy, mix the data to construct `stage1.json` and `stage2.json` for the pre-training and instruction fine-tuning phases.  

**Step 3.** Replace the corresponding files under the `Qwen2.5-3B-Instruct` folder with the scripts in **`ChatTS-Components`**. If the files do not exist, simply paste them in.  

**Step 4.** Follow the training instructions in [ChatTS-Training](https://github.com/xiezhe-24/ChatTS-Training). Make sure to specify the dataset information in `dataset_info.json`.  

**Step 5.** Once training is complete, use **`eval_model.py`** and **`cal_acc.py`** from the **`Test-Scripts`** folder to evaluate the model and calculate accuracy.  

---
