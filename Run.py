import os
import pandas
import numpy
import json
import copy
import random
from LlmModel import status_logger, LLM_Model
# import LlmModel

import re  # 用来规则替换xml文中中内容
import Agent
from Agent import ExtractionAgent, EvaluateAgent, SchemaGenerateAgent, SyncReasonAgent, TransformAgent

import time


std_p = "/remote-home/iot_wangrongkai/LLM-code/Text2UA-git/Test_data/ST-data/"
nstd_p = "/remote-home/iot_wangrongkai/LLM-code/Text2UA-git/Test_data/NST-data/"
mixd_p = "/remote-home/iot_wangrongkai/LLM-code/Text2UA-git/Test_data/MIX_data/"

r_tuples_p = "/remote-home/iot_wangrongkai/LLM-code/Text2UA-git/Result/Tuples/"
r_eval_p = "/remote-home/iot_wangrongkai/LLM-code/Text2UA-git/Result/Evaluate/"
r_schema_p = "/remote-home/iot_wangrongkai/LLM-code/Text2UA-git/Result/Scheme/"
r_sync_p = "/remote-home/iot_wangrongkai/LLM-code/Text2UA-git/Result/Sync/"
r_sync_reason_p = "/remote-home/iot_wangrongkai/LLM-code/Text2UA-git/Result/SyncReason/"
r_xml_p = "/remote-home/iot_wangrongkai/LLM-code/Text2UA-git/Result/XML/"
r_time_p = "/remote-home/iot_wangrongkai/LLM-code/Text2UA-git/Result/Time/"

filename_dict = {
    "std":{
        # "a1":"Actuator1",
        # "a2":"Actuator2",
        # "c1":"Controller1",
        # "c2":"Controller2",
        # "s1":"Sensor1",
        # "s2":"Sensor2",
        # "co1":"Connectivity1",
        # "co2":"Connectivity2",  
    },
    "nstd":{                     
        # "abb":"ABB", 
        # "abb-z":"ABB_ZH",    # Chinese is not good
        "fanuc":"FANUC",    
        # "fanuc-z":"FANUC_ZH",  
        # "kuka":"KUKA",
        # "kuka-z":"KUKA_ZH",  
        # "yaskawa":"YASKAWA",
        # "yaskawa-z":"YASKAWA_ZH",
        # "reactor":"Reactor",
        # "reactor-z":"Reactor_ZH",
        # "boiler":"Boiler",  # 
        # "boiler-z":"Boiler_ZH",# 
        # "distillator":"Distillator",
        # "distillator-z":"Distillator_ZH",   
        # "extractor":"Extractor",  # 
        # "extractor-z":"Extractor_ZH",# 
    }
}

model_config = {
            # 'gpt-3.5-turbo-instruct': ("gpt-3.5-turbo-instruct", 2700),
            'gpt-3.5-turbo-instruct': ("gpt-3.5-turbo", 4046),
            'llama-3.1-405b-instruct':("meta/llama-3.1-405b-instruct",4046),
            'qwen-turbo': ("qwen-turbo", 2000),    # qwen-long 试试？  TODO 次数很少，就试一次！
            'gpt-4o-mini-2024-07-18': ("gpt-4o-mini", 4046),
            # 'Llama_2_70B_HF': ('meta-llama/Llama-2-70b-hf', 2000),
        }

"""
Init
"""
LLMmodel = LLM_Model(env_file='.env.gpt')  # LLM-API
# LLMmodel = LLM_Model(env_file='.env.llama')  
# LLMmodel = LLM_Model(env_file='.env.qianwen')  

# 0-gpt35 + 1-llama31  + 2-qwen + 3-gpt4omini 
model_name = list(model_config.keys())[0] # choose name
if model_name in ['gpt-3.5-turbo-instruct']:
    f_suffix = '-gpt'
elif model_name in ['llama-3.1-405b-instruct']:
    f_suffix = '-llama'
elif model_name in ['gpt-4o-mini-2024-07-18']:
    f_suffix = '-gpt4o'
elif model_name in ['qwen-turbo']:
    f_suffix = '-qianwen'


extraction_agent = ExtractionAgent(LLMmodel) 
eval_agent = EvaluateAgent(LLMmodel)
eval_time = 3  
schema_agent = SchemaGenerateAgent(LLMmodel)
sync_agent = SyncReasonAgent(LLMmodel)  
xml_agent = TransformAgent(LLMmodel)

"""
Main
"""
for ii in range(1):  # 只跑一遍
    
    for d_type in filename_dict:  
        if d_type == "std":
            pth_prex = std_p
        elif d_type == "nstd":
            pth_prex = nstd_p
        elif d_type == "mix":
            pth_prex = mixd_p
        
        for f_name in filename_dict[d_type]:  
            
            t_begin = time.time()  
            
            # ========================IES============================================
            
            source_text_p = f"{pth_prex}{filename_dict[d_type][f_name]}.txt"
            print(source_text_p)
            source_text = extraction_agent.read_input_txt(source_text_p)
            print(source_text)
            # break
            tuples_dict = extraction_agent.generate_output(input_text=source_text,
                                                            model=model_name)    
            extraction_agent.save_output_json(pth=f"{r_tuples_p}{filename_dict[d_type][f_name]}{f_suffix}.json",
                                            out=tuples_dict)   
            print(f"{filename_dict[d_type][f_name]}{f_suffix}: tuples_dict = {tuples_dict} \n")
            
            tuples_dict_1 = tuples_dict 
            
            # ==================ESA=====================================================
            for i in range(eval_time):
                extraction_agent.save_output_json(pth=f"{r_eval_p}{filename_dict[d_type][f_name]}{f_suffix}-fill-{i}.json",
                                                out=tuples_dict_1)

                tuples_dict_2 = extraction_agent.generate_output(input_text=source_text,
                                                                model=model_name)    
                extraction_agent.save_output_json(pth=f"{r_eval_p}{filename_dict[d_type][f_name]}{f_suffix}-comp-{i}.json",
                                                out=tuples_dict_2)    
                # print(f"{filename_dict[d_type][f_name]}{f_suffix}: tuples_dict = {tuples_dict} \n")
                
                
                eval_dict = eval_agent.generate_output(input_tuple1=tuples_dict_1,   
                                                        input_tuple2=tuples_dict_2,   
                                                        model=model_name)    
                eval_agent.save_output_json(pth=f"{r_eval_p}{filename_dict[d_type][f_name]}{f_suffix}-final-{i}.json", out=eval_dict)
                print(f"{filename_dict[d_type][f_name]}{f_suffix}: eval_dict = {eval_dict} \n")
                eval_agent.save_embeddings_list_npy(pth=f"{r_eval_p}{filename_dict[d_type][f_name]}{f_suffix}-embeddingsForAllObjMethod-{i}.npy") #
                
                tuples_dict_1 = eval_dict  
            
            tuples_dict = eval_dict
            
            try:
                meta_Sub = tuples_dict["tuples"][0]["SubjectEntity_1"]["Name"]  
            except:    
                all_values = tuples_dict["tuples"][0].values()  
                # print(all_values)
                first_name_dict = next(item for item in all_values if "Name" in item)  
                
                meta_Sub = first_name_dict["Name"]  
            print(f"Now meta_sub is {meta_Sub} \n")
            
            
            
            # ================SGA====================================================
            schema_dict = schema_agent.generate_output(input_text=meta_Sub,
                                                        model=model_name)   
            schema_agent.save_output_json(pth=f"{r_schema_p}{filename_dict[d_type][f_name]}{f_suffix}.json",
                                            out=schema_dict)
            print(f"{filename_dict[d_type][f_name]}{f_suffix}: schema_dict = {schema_dict} \n")
            
               
            # ================SA======================================================
        
            input_schema_p = f"{r_schema_p}{filename_dict[d_type][f_name]}{f_suffix}.json"
            input_schema = sync_agent.read_input_json(input_schema_p)

            input_tuples_p = f"{r_eval_p}{filename_dict[d_type][f_name]}{f_suffix}-final-{(eval_time-1)}.json"
            input_tuples = sync_agent.read_input_json(input_tuples_p)

            sync_dict = sync_agent.generate_output(input_schema=input_schema,
                                                    input_tuples=input_tuples,
                                                    model=model_name)   
            sync_agent.save_reason_json(pth=f"{r_sync_reason_p}{filename_dict[d_type][f_name]}{f_suffix}-reason.json") 
            sync_agent.save_output_json(pth=f"{r_sync_p}{filename_dict[d_type][f_name]}{f_suffix}.json", out=sync_dict)
            print(f"{filename_dict[d_type][f_name]}{f_suffix}: sync_dict = {sync_dict} \n")
            
            
            # ==============FTA=======================================================
            opcua_schema_p = f"{r_sync_p}{filename_dict[d_type][f_name]}{f_suffix}.json"
            opcua_schema = xml_agent.read_input_json(opcua_schema_p)
            
            xml_final = xml_agent.generate_output(input_json=opcua_schema,
                                                    model=model_name)    
            xml_agent.save_output_xml(pth=f"{r_xml_p}{filename_dict[d_type][f_name]}{f_suffix}.xml",
                                            out=xml_final)
            print(f"{filename_dict[d_type][f_name]}{f_suffix}: xml_final = {xml_final} \n")
            
        
            """LOG"""   
            # logg = status_logger.get_logs(f"log-{filename_dict[d_type][f_name]}{f_suffix}.txt")
            # # print("\n logg = ", logg)
            
            # with open(f"{r_time_p}{filename_dict[d_type][f_name]}{f_suffix}-all-time.txt", 'w') as file:  
            #     file.write(str(time.time() - t_begin)) 





   
    

   
   
   
   

        
        
    
    
    
    



























