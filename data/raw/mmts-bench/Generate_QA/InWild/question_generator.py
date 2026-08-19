import base64
import os
import json
from pathlib import Path
from utils.openai_client import OpenAIClient
import re
from tqdm import tqdm
import random
import logging

# Initialize the large language model
api_config = {
    "api_key": "YOUR_API_KEY_HERE",
    "base_url": "YOUR_API_BASE_URL_HERE",
    "model": "gpt-4o", # claude-3.7-sonnet
    "temperature": 0.7,
    "max_tokens": 8192
}

openai_client = OpenAIClient(
        api_config=api_config,
        max_retries=3,    # Number of retries
        timeout=30,       # Timeout duration
        rate_limit_rpm=120  # RPM limit
    )

TEST_MODE = True  # Set to True to process only partial data
# Path to images folder
img_path = Path('./data/images')

def load_images_to_dict(folder_path):
    """Convert all supported images in the folder to base64 and store in dictionary"""
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    images_dict = {}
    
    folder = Path(folder_path)
    for file_path in folder.iterdir():
        if file_path.is_file() and any(file_path.suffix.lower() == ext for ext in image_extensions):
            try:
                images_dict[file_path.stem] = get_image_base64(file_path)
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
    
    return images_dict

def get_image_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    
images_dict = load_images_to_dict(img_path)

# Checkpoint resume functionality
class ConversationSaver:
    def __init__(self, file_path):
        self.file_path = file_path
        # Check if file exists and try to load
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.all_conversations = json.load(f)
                print(f"Loaded {len(self.all_conversations)} existing conversations from {file_path}")
        except (FileNotFoundError, json.JSONDecodeError):
            # File doesn't exist or is empty, initialize as empty list
            self.all_conversations = []
            # Create empty file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('[]')
            print(f"Initialized new conversation file at {file_path}")
    
    def save(self, conversation_record):
        # Use data in memory directly to reduce file I/O
        self.all_conversations.append(conversation_record)
        
        # Use temporary file to ensure atomic write operation, avoid file corruption from program crash
        temp_file = f"{self.file_path}.temp"
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(self.all_conversations, f, ensure_ascii=False, indent=4)
        
        # Safely replace original file
        os.replace(temp_file, self.file_path)
        print(f"Saved record with ID: {conversation_record['id']}. Total records: {len(self.all_conversations)}")
    
    def get_all(self):
        # Return data from memory directly instead of reading from file each time
        return self.all_conversations
            
    def get_processed_ids(self):
        """Get list of processed IDs"""
        # Extract ID list from memory to avoid repeated file reads
        return [conv["id"] for conv in self.all_conversations]
        
    def count(self):
        """Return the number of currently saved conversations"""
        return len(self.all_conversations)
    
    
# Read meta data JSON file
with open('./data/traffic_meta.json', 'r') as f:
    data = json.load(f)

# Read statistical metric description file
with open('./config/describe_config.json', 'r') as f:
    describe_config = json.load(f)

def question_generator(data, describe_config, images_dict, use_single_feature=False):

    # Initialize saver
    save_path = "./output/all_conversations.json"
    saver = ConversationSaver(save_path)

    # Get list of processed IDs
    processed_ids = set(saver.get_processed_ids())
    
    # Test mode:
    if TEST_MODE:
        data = data[0:2]  # Keep only partial data items
        # print(data)

    for item in tqdm(data, desc="Generating QA pairs", unit="item"):
        # Extract variables
        domain = item["domain"]
        start_index = item["start_index"]
        end_index = item["end_index"]
        length = end_index - start_index + 1
        numerical_data = item["value"]
        image_name = str(item["id"])
        task_type = item["task_type"]
        qa_type = item["qa_type"]
        sample_interval = item["freq"] 
        local_overall = item["local_overall"]

        # Skip if already processed
        if image_name in processed_ids:
            print(f"Skipping already processed item: {image_name}")
            continue
        
        # Extract features and results
        features_dict = item["features"]["ts1"].get(task_type, {})  # Empty dict if no features
        features = " & ".join(features_dict.keys())
        result = ", ".join([f'"{k}": {v}' for k, v in features_dict.items()])

        # Decide whether to use single feature or all features based on parameter
        if use_single_feature and features_dict:
            # Randomly select one feature
            feature_name = random.choice(list(features_dict.keys()))
            selected_features_dict = {feature_name: features_dict[feature_name]}
            features = feature_name
            result = f'"{feature_name}": {features_dict[feature_name]}'
        else:
            # Use all features
            selected_features_dict = features_dict
            features = " & ".join(features_dict.keys())
            result = ", ".join([f'"{k}": {v}' for k, v in features_dict.items()])
        
        # Extract feature explanations
        features_explanations = []
        if "task_type" in describe_config and task_type in describe_config["task_type"]:
            config_features = describe_config["task_type"][task_type]
            task_type_explanation = describe_config["task_type"][task_type][task_type]
            for feature_name in selected_features_dict.keys():
                if feature_name in config_features:
                    features_explanations.append(f"{feature_name}:{config_features[feature_name]}")

        # Combine feature explanations into a single string
        features_explanation_text = " ".join(features_explanations)

        ##################################################### first round conversation ##########################################################
        message_1 = [
            {"role": "system",
            "content": "You are a time series expert, your task is to generate time series description based on the provided time series data and charts according to user requirements."},
            {"role": "user",
            "content": f"Here is the time series data for {domain}, with a length of {length} and a sampling frequency of {sample_interval}. The numerical data in list form is: {numerical_data}"
            },
            {"role": "user",
            "content": [
                {"type": "text", "text": "The chart of this time series is as follows:"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{images_dict.get(image_name)}"}}
            ]
            },
            {"role": "user",
            "content": f"The user performed calculations on this time series using metrics such as {features}, yielding the following results: {result}. {features_explanation_text}"
            },
            {"role": "user",
            "content": f"Based on the provided information, generate a detailed description of this time series regarding {task_type}. {task_type_explanation}"
            }
        ]

        response_1_raw = openai_client.generate_response(messages=message_1)
        response_1 = response_1_raw.choices[0].message.content
        logging.info('-----------------------First round conversation response-----------------------')
        logging.info(response_1)

        ###################################################### second round conversation ##########################################################
        raw_qa = response_1

        # Calculate day of week concept using index
        def calculate_datetime(index):
            # Base time: January 1, 2015 at 00:00, Thursday
            base_weekday = 3  # 0 is Monday, 1 is Tuesday, ..., 6 is Sunday, so Thursday is 3
            hours_passed = index  # Since sampling frequency is 1H, index equals hours passed
            # Calculate days passed and remaining hours
            days_passed = hours_passed // 24
            remaining_hours = hours_passed % 24
            # Calculate day of week
            weekday = (base_weekday + days_passed) % 7
            weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            weekday_name = weekday_names[weekday]
            # Calculate hour
            hour = remaining_hours
            return weekday_name, hour
        
        # Convert index to day of week and hour concept
        strat_weekday, start_hour = calculate_datetime(start_index)
        end_weekday, end_hour = calculate_datetime(end_index)

        # Select different requirements based on local_overall
        if local_overall == "local":
            requirements_local = f'''
            1. Updated issues must be clear, accurate, and unambiguous.
            2. Use the provided {features_explanation_text} metrics to focus on updating issues for the {task_type} task.
            3. The time series values, charts, and calculated feature values provided by the user are based on segments of the original sequence. The data provided by the user is a segment of length {length}. However, your perspective in creating Q&A pairs should address local questions posed against the original time series.
            4. The time series segment starts with an index value of {start_index} (corresponding to the timestamp {strat_weekday} at {start_hour}) and ends with an index value of {end_index} (corresponding to the timestamp {end_weekday} at {end_hour}), used to specify the time series segment in question.
            5. The index in the question must be annotated with its corresponding timestamp. If two indexes correspond to the same day of the week, they must be distinguished in the description.
            6. The exact values of the relevant indicators user provide to you should not appear directly in the question but can be included as part of the answer.
            7. Assume that respondents can only access raw time series data and images.
            8. Provide accurate answers based on updated questions using a three-part (question, answer, explanation) response template, starting each section with **Question**, **Answer**, and **Explanation** respectively.
            9. Fabrication of content is prohibited.
            '''
            requirements_2 = requirements_local
        else:  # local_overall == "overall"
            requirements_overall = f'''
            1. Updated issues must be clear, accurate, and unambiguous.
            2. Use the provided {features_explanation_text} metrics to focus on updating issues for the {task_type} task.
            3. The timestamp corresponding to {start_index} is {strat_weekday} at {start_hour}, and the timestamp corresponding to {end_index} is {end_weekday} at {end_hour}.
            4. If the problem you create requires the use of indices, it is necessary to specify which day of the week and what time each index points to. If two indices point to the same day of the week, a brief description must be provided to distinguish them.
            5. The exact values of the relevant indicators user provide to you should not appear directly in the question but can be included as part of the answer.
            6. Assume that respondents can only access raw time series data and images.
            7. Provide accurate answers based on updated questions using a three-part (question, answer, explanation) response template, starting each section with **Question**, **Answer**, and **Explanation** respectively.
            8. Fabrication of content is prohibited.
            '''
            requirements_2 = requirements_overall

        message_2=[
            {"role": "system",
                "content": "You are a time series expert, and your task is to create Q&A pairs based on the provided time series data, relevant statistical values, and other related information, ensuring that the Q&A pairs are reasonable and accurate."},
            {"role": "user",
                "content": f"Here is the time series data for {domain}, with a length of {length} and a sampling frequency of {sample_interval}. The numerical data in list form is: {numerical_data}"
            },
            {"role": "user",
            "content": [
                {"type": "text", "text": "The chart of this time series is as follows:"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{images_dict.get(image_name)}"}}
            ]
            },
            {"role": "user",
                "content": f"The user performed calculations on this time series using metrics such as {features}, yielding the following results: {result}. {features_explanation_text}"
            },
            {"role": "user",
                "content": f"Based on the above time series numerical data, charts, and feature indicator values, the user has provided the following description of this time series segment regarding {task_type}: <{raw_qa}>"
            },
            {"role": "user",
                "content": f"Now you need to generate a Q&A pair based on the user's provided description. The additional requirements are as follows: {requirements_2}"
            },
        ]

        response_2_raw = openai_client.generate_response(messages=message_2)
        response_2 = response_2_raw.choices[0].message.content
        logging.info('-----------------------Second round conversation response-----------------------')
        logging.info(response_2)

        ###################################################### third round conversation ##########################################################
        # Extract qa_type explanation
        qa_type_explanations = []
        if "qa_type" in describe_config and qa_type in describe_config["qa_type"]:
            config_qa_type = describe_config["qa_type"][qa_type]
            qa_type_explanations.append(config_qa_type)
            qa_type_explanation_text = "".join(qa_type_explanations)

        evol_qa = response_2
       
        requirements_3 = f'''
        1. The newly generated questions must require observing charts or performing relevant calculations using raw numerical data to be answered correctly.
        2. The incorrect options should be somewhat misleading, but there should still be only one correct option.
        3. The start index value of the time series segment is {start_index} (corresponding to the timestamp {strat_weekday} at {start_hour}), and the end index value is {end_index} (corresponding to the timestamp {end_weekday} at {end_hour}). Any used index must be accompanied by its corresponding timestamp.
        4. All indices appearing in the user-provided question-answer pairs must be retained.
        5. Use a four-part response template (question, options, correct answer, brief explanation), with **Question**, **Options**, **Correct Answer**, **Brief Explanation** as headers for each part in the response.
        6. Feature indicator names and ranges can appear indirectly in questions and answers, but the exact numerical values of feature indicators provided by users must not be used directly.
        7. Reflect and self-check the Q&A pairs generated for you without outputting the reflection and checking process.
        8. Do not fabricate or imagine content.
        '''

        message_3=[
            {"role": "system",
                "content": "You are a time series expert, statistics expert, and large language model performance testing expert. You need to collaborate with the user to create time series question-answer pairs."
            },
            {"role": "user",
                "content": f"Here is the time series data for {domain}, with a length of {length} and a sampling frequency of {sample_interval}. The numerical data in list form is: {numerical_data}"
            },
            {"role": "user",
            "content": [
                {"type": "text", "text": "The chart of this time series is as follows:"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{images_dict.get(image_name)}"}}
            ]
            },
            {"role": "user",
                "content": f"The user performed calculations on this time series using metrics such as {features}, yielding the following results: {result}. {features_explanation_text}"
            },    
            {"role": "user",
                "content": f"Based on the above time series numerical data, charts, and characteristic indicator values, the user has preliminarily generated a raw Q&A pair regarding {task_type}:{evol_qa}"
            },
            {"role": "user",
                "content": f"Now, you need to construct {qa_type} type Q&A pairs, which are defined as: {qa_type_explanation_text}."
            },
            {"role": "user",
                "content": f"Supplementary requirements are as follows: {requirements_3}"
            }
        ]

        response_3_raw = openai_client.generate_response(messages=message_3)
        response_3 = response_3_raw.choices[0].message.content
        logging.info('-----------------------Third round conversation response-----------------------')
        logging.info(response_3)

        # Create a dictionary to store all information from current iteration
        conversation_record = {
            "id": image_name,
            "message_1": message_1,
            "response_1": response_1,
            "message_2": message_2,
            "response_2": response_2,
            "message_3": message_3,
            "response_3": response_3
        }
        
        # Add current record to list
        saver.save(conversation_record)

    return saver.get_all()

# Call question_generator function
all_conversations = question_generator(data, describe_config, images_dict, use_single_feature=True)
print(f"Total generated {len(all_conversations)} conversations")

# Extract questions, options, and answers from the key information of the last round of conversation in the history, and generate the final dataset JSON file
def extract_and_fill_data(all_conversations_path, target_json_path, output_path):
    # Load JSON file containing all conversations
    with open(all_conversations_path, 'r', encoding='utf-8') as f:
        all_conversations = json.load(f)
    
    # Load target JSON file
    with open(target_json_path, 'r', encoding='utf-8') as f:
        target_data = json.load(f)
    
    # Create mapping from ID to conversation
    conversations_dict = {conv["id"]: conv for conv in all_conversations}
    
    # Regular expression patterns
    question_pattern = r"\*\*Question\*\*(.*?)(?=\n\n\*\*Options\*\*|\Z)"
    options_pattern = r"\*\*Options\*\*(.*?)(?=\n\n\*\*Correct Answer\*\*|\Z)"
    answer_pattern = r"\*\*Correct Answer\*\*(.*?)(?=\n\n\*\*Brief Explanation\*\*|\Z)"
    
    # Iterate through target data and fill content
    for item in target_data:
        item_id = item.get("id")
        if item_id in conversations_dict:
            response_3 = conversations_dict[item_id]["response_3"]
            
            # Extract question
            question_match = re.search(question_pattern, response_3, re.DOTALL)
            if question_match:
                item["question"] = question_match.group(1).strip()
            
            # Extract options
            options_match = re.search(options_pattern, response_3, re.DOTALL)
            if options_match:
                item["option"] = options_match.group(1).strip()
            
            # Extract correct answer
            answer_match = re.search(answer_pattern, response_3, re.DOTALL)
            if answer_match:
                item["answer"] = answer_match.group(1).strip()
    
    # Save updated target JSON file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(target_data, f, ensure_ascii=False, indent=4)
    
    print(f"Data successfully extracted and filled to {output_path}")

# Usage example
all_conversations_path = "./output/all_conversations.json"
target_json_path = './data/traffic_meta.json'  # Replace with your target JSON file path
output_path = './output/traffic_qa.json'  # Replace with the path where you want to save the results

extract_and_fill_data(all_conversations_path, target_json_path, output_path)