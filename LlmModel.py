import openai
from openai import OpenAI
import os
from collections import deque
from datetime import datetime
from dotenv import load_dotenv,find_dotenv
# from sentence_transformers import SentenceTransformer, util
import json

"""用于记录你运行时的log"""
class StatusLogger:
    def __init__(self, max_size=200):
        self.log_queue = deque(maxlen=max_size) 

    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.log_queue.append(formatted_message) 

    def get_logs(self, pth="logs.txt"):  
        logs = list(self.log_queue)
        with open(pth, "a") as file:  
            for log in logs:  
                file.write(log + "\n")  
        
        self.log_queue.clear()  
        return logs
    
status_logger = StatusLogger()  

gpt_call_count = 0

class LLM_Model:
    def __init__(self, env_file):
        
        if env_file == '.env.gpt':
            _ = load_dotenv(find_dotenv('.env.gpt'))
        elif env_file == '.env.llama':
            _ = load_dotenv(find_dotenv('.env.llama'))
        elif env_file == '.env.qianwen':
            _ = load_dotenv(find_dotenv('.env.qianwen'))
                   
        self.client = OpenAI() 
        
        
    def llm_model_call(self, prompt, input_text, model='gpt-3.5-turbo-instruct'):
    
        model_config = {
            # 'gpt-3.5-turbo-instruct': ("gpt-3.5-turbo-instruct", 2700),
            'gpt-3.5-turbo-instruct': ("gpt-3.5-turbo", 4046),
            'llama-3.1-405b-instruct':("meta/llama-3.1-405b-instruct",4046),
            'qwen-turbo': ("qwen-turbo", 2000),   
            'gpt-4o-mini-2024-07-18': ("gpt-4o-mini", 4046),
            # 'Llama_2_70B_HF': ('meta-llama/Llama-2-70b-hf', 2000),
        }
        model_name, max_tokens = model_config.get(model)
        print(f"model_name={model_name}, max_tokens={max_tokens}\n")
        
        self.sampling_params = \
        {
            "max_tokens": max_tokens, 
            "temperature": 0, 
            # "top_p":
            "n": 1, 
            # "presence_penalty": 0.5, 
            # "frequency_penalty": 0.3, 
            # "stop": ['\n']
        }

        global gpt_call_count
        gpt_call_count += 1

        status_logger.log(f" start LLM generation, count #{gpt_call_count}")  
        
        
        if model_name == "qwen-turbo":
            try:
                # model_response = openai.Completion.create(
                model_response = self.client.chat.completions.create(
                    model=model_name,
                    # response_format={ "type": "json_object" },  
                    messages=[
                            # {"role": "system","content": prompt},
                              {"role": "user","content": prompt}   
                            ],
                    # message=prompt,
                    temperature=0,   
                    max_tokens=max_tokens,
                    stream=True  
                    # **self.sampling_params
                )
                print(f"Now: model is {model_name}")
                # model_output = model_response.choices[0].message 
            except Exception as e:
                # Handle exceptions that might occur during the GPT model call
                # status_logger.log(f"Error during GPT model call: {e}")
                status_logger.log(f"Error during LLM model call")
                return None 
        else:
            try:
                # model_response = openai.Completion.create(
                model_response = self.client.chat.completions.create(
                    model=model_name,
                    # response_format={ "type": "json_object" },  
                    messages=[
                            {"role": "system","content": prompt},
                            #   {"role": "user","content": input_text}
                            ],
                    # message=prompt,
                    temperature=0,   
                    max_tokens=max_tokens,
                    stream=True  
                    # **self.sampling_params
                )
                print(f"Now: model is {model_name}")
                # model_output = model_response.choices[0].message
            except Exception as e:
                # Handle exceptions that might occur during the GPT model call
                # status_logger.log(f"Error during GPT model call: {e}")
                status_logger.log(f"Error during LLM model call")
                return None 
                
            
        status_logger.log(f" GPT generation finished, count #{gpt_call_count}")
        
        self.model_response = model_response
        # return model_output
        return model_response
    
    def save_stream_data(self, f_name):
        # 初始化一个空字符串，用于保存完整的响应数据  
        complete_response = "" 
        for chunk in self.model_response:
            if chunk.choices[0].delta.content is not None:
                print(chunk.choices[0].delta.content, end="")  
                complete_response += chunk.choices[0].delta.content  
  
    
        # print(complete_response)  
        # Parse the text output into a JSON object
        # tuples_dict = json.loads(complete_response.strip())  
        # print(tuples_dict)
        with open(f'{f_name}.txt', 'w') as file:  
            file.write(complete_response)


