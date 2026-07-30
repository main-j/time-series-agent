# TS-LLMs Evaluation Scripts

This repository contains scripts for testing and evaluating three open-source TS-LLMs: **ChatTS**, **ITFormer**, and **ChatTime**.  
The code is organized into separate folders named after each model.  

- **`./ChatTS`**: Evaluation scripts for ChatTS  
- **`./ITFormer`**: Evaluation scripts for ITFormer  
- **`./ChatTime`**: Evaluation scripts for ChatTime  
- **`./utils`**: Utility functions that are required for evaluation. Copy them into the corresponding model folders.

---

## How to Run ChatTS Evaluation

**Step 1.** Download model weights from the [ChatTS official model repository](https://huggingface.co/bytedance-research/ChatTS-14B).  

**Step 2.** Modify the model path, dataset subset path, and other configurations in `eval_chatts.py`, then run the script to start evaluation.  

**Step 3.** Use `cal_acc.py` and `cal_num.py` to compute the model’s performance on **choice** and **numerical** tasks, respectively.  

---

## How to Run ITFormer Evaluation

**Step 1.** Clone the [ITFormer official GitHub repository](https://github.com/Pandalin98/ITFormer-ICML25) to your local environment.  

**Step 2.** Download the model weights (0.5B, 3B, and 7B versions) from the [ITFormer model repository](https://huggingface.co/pandalin98).  

**Step 3.** Copy `eval_itformer.py` into the project folder, and replace the original `dataset.py` and `infer.yaml` files in the **ITFormer-ICML25** folder with the provided ones.  

**Step 4.** Modify the model path, dataset subset path, and other configurations in `eval_itformer.py`, then run the script to start evaluation.  

**Step 5.** Use `cal_acc.py` and `cal_num.py` to compute the model’s performance on **choice** and **numerical** tasks, respectively.  

---

## How to Run ChatTime Evaluation

**Step 1.** Clone the [ChatTime official GitHub repository](https://github.com/ForestsKing/ChatTime) to your local environment.  

**Step 2.** Download model weights from the [ChatTime model repository](https://huggingface.co/ChengsenWang/ChatTime-1-7B-Chat).  

**Step 3.** Replace the original `model.py` file with the provided one.  

**Step 4.** Modify the model path, dataset subset path, and other configurations in `eval_chattime.py`, then run the script to start evaluation.  

---
