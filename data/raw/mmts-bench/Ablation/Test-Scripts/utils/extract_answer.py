from utils.llms.open_sourced import load_llm_model, llm_generate

tokenizer, model = load_llm_model("Qwen2.5-7B-Instruct", device=0)

def extract_answer(question, options, gpt_answer, question_type="choice"):
    system_prompt = "You are a helpful assistant. Please help the user extract the final answer from a raw answer carefully."
    if question_type == "choice":
        user_prompt=f"""Now I will provide you with a question and the options, as well as a raw answer. Your task is to extract the final answer from the raw answer, the final answer should be one from the options.

Question: \n{question}
Options: \n{options}
Raw answer: \n{gpt_answer}

You must output in the following format:

Final answer is : <the answer(A,B,C,D...)>

Don't output anything else, except the single sentence above.
"""
    elif question_type == "numerical":
        user_prompt=f"""Now I will provide you with a question, as well as a raw answer from a gpt. Your task is to extract the final answer from the raw answer, the final answer should be in single value.

Question: \n{question}
Raw answer: \n{gpt_answer}

You must output in the following format:

Final answer is : <value>

Don't output anything else, except the single sentence above.
"""

    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    response = llm_generate(tokenizer, model, messages)

    return response


# ----------------- TEST ----------------- #
# question = "The seasonality analysis of the sequence can be performed using seasonal_strength as a reference metric. The calculation method is seasonal_strength is as follows: The `seasonal_strength` feature quantifies seasonality strength as \\( 1 - \\frac{\\mathrm{Var}(R_t)}{\\mathrm{Var}(S_t + R_t)} \\), where \\( S_t \\) and \\( R_t \\) are the seasonal and remainder components. Higher values indicate stronger seasonal patterns. Now, please answer the following question: Based on the weekly time series data, which statement most accurately describes the seasonal characteristics of this data?"
# options = "A) The time series exhibits strong seasonal patterns with consistent quarterly cycles and predictable seasonal fluctuations.\nB) The time series shows minimal seasonal correlation, suggesting that values in one quarter have little predictive relationship with values in the same quarter of different years.\nC) The time series demonstrates a strong positive seasonal autocorrelation, indicating that values in one quarter are strongly correlated with values in the same quarter of different years.\nD) The time series displays regular quarterly patterns with consistent amplitude throughout the entire period of observation."
# raw_answer = "The seasonal_strength for the weekly time series data is 0.00, indicating no detectable seasonal patterns. The time series has a length of 78 points, with no periodic fluctuations observed. The overall trend is decreasing, starting from around 4081.25 and ending at around 2226.09, with an amplitude of -1855.17. The mean value of the time series is 2654.9, and the minimum and maximum values are 4550.97 (around point 0) and 1823.02 (around point 77), respectively. The time series has a noisy nature, with a standard deviation of approximately 39.23, indicating a large amount of random variation. No local characteristics are found in the data, and there are no significant spikes or drops observed. Additionally, no periodic fluctuations are present, confirming the absence of seasonal patterns. Given these observations, the correct answer is B) The time series shows minimal seasonal correlation, suggesting that values in one quarter have little predictive relationship with values in the same quarter of different years."

# answer = extract_answer(question, options, raw_answer)
# print(answer)