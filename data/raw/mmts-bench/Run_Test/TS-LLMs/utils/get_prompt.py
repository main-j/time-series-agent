import numpy as np

def get_prompt_content(question: str, option: str, question_type="choice") -> str:
    # if "tsqa" in dataset_name or "ts2caption_qa" in dataset_name:
    if question_type == "choice":
        background = "Please carefully analyze the question, consider the given value and options, then provide your answer at the end."
        prompt_content = f"""Please answer the following question based on the given information.

Question: {question}
Options: {option}

{background}

Please output in the following format, so that I can better extract your answer:

<thinking_process>
[Write your analysis and reasoning process inside here]
</thinking_process>

<final_answer>
[Write your final answer inside here, must in A,B,C,D...]
</final_answer>"""
        
    else:
        background = "Please carefully analyze the question, consider the given time series value, then provide your answer (in single value) at the end."
        prompt_content = f"""Please answer the following question based on the given information.

Question: {question}

{background}

Please output in the following format, so that I can better extract your answer:

<thinking_process>
[Write your analysis and reasoning process inside here]
</thinking_process>

<final_answer>
[Write your final answer inside here, must in single value]
</final_answer>"""

    return prompt_content


def get_full_prompt(ts:list, prompt_content, dataset_name):
    flag = True # if len of arr <64 or >1024, quit

    if any(isinstance(i, np.ndarray) for i in ts) and len(ts) > 1:
        prefix = f"I have {len(ts)} time series:\n"
        for i,arr in enumerate(ts):
            prefix += f"The time series {str(i+1)} is of length {len(arr)}: <ts><ts/>\n"
            if len(arr) < 64 or len(arr) > 1024:
                flag = False
                break
    else:
        arr = ts[0]
        prefix = "I have 1 time series:\n"
        prefix += f"The time series is of length {len(arr)}: <ts><ts/>\n"
        if len(arr) < 64 or len(arr) > 1024:
            flag = False

    # if "tsqa" in dataset_name:
    #     if any(isinstance(i, list) for i in ts):
    #         prefix = f"I have {len(ts)} time series:\n"
    #         for i,arr in enumerate(ts):
    #             prefix += f"The time series {str(i+1)} is of length {len(arr)}: <ts><ts/>\n"
    #             if len(arr) < 64 or len(arr) > 1024:
    #                 flag = False
    #                 break
    #     else:
    #         prefix = "I have 1 time series:\n"
    #         prefix += f"The time series is of length {len(ts)}: <ts><ts/>\n"
    #         if len(ts) < 64 or len(ts) > 1024:
    #             flag = False
    
    # elif "ts2caption_qa" in dataset_name:
    #     if any(isinstance(i, list) for i in ts):
    #         prefix = f"I have {len(ts)} time series:\n"
    #         for i,arr in enumerate(ts):
    #             prefix += f"The ts{str(i+1)} is of length {len(arr)}: <ts><ts/>\n"
    #             if len(arr) < 64 or len(arr) > 1024:
    #                 flag = False
    #                 break
    #     else:
    #         prefix = "I have 1 time series:\n"
    #         prefix += f"The ts1 is of length {len(ts)}: <ts><ts/>\n"
    #         if len(ts) < 64 or len(ts) > 1024:
    #             flag = False

    # elif "qats" in dataset_name or "caption2ts_qa" in dataset_name:
    #     if any(isinstance(i, list) for i in ts):
    #         prefix = f"I have {len(ts)} time series:\n"
    #         for i,arr in enumerate(ts):
    #             prefix += f"The ts{str(i)} is of length {len(arr)}: <ts><ts/>\n"
    #             if len(arr) < 64 or len(arr) > 1024:
    #                 flag = False
    #                 break
    #     else:
    #         prefix = "I have 1 time series:\n"
    #         prefix += f"The ts0 is of length {len(ts)}: <ts><ts/>\n"
    #         if len(ts) < 64 or len(ts) > 1024:
    #             flag = False

    # else:
    #     print("Error: dataset_name not recognized.")
        
    prompt = f"""full_prompt = f"<|im_start|>system\nYou are a helpful assistant. Your name is ChatTS. You can analyze time series data and provide insights. If user asks who you are, you should give your name and capabilities in the language of the prompt.<|im_end|><|im_start|>user\n{prefix}{prompt_content} Please output a analysis about the time series attributes that mentioned in the question first, and then give a detailed result about this question. Always remember to carefully double check the values before answer the results.<|im_end|><|im_start|>assistant\n"
"""
    return flag, prefix, prompt