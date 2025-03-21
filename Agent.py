import os
import pandas
import numpy
import json
import copy
import random
from LlmModel import status_logger, LLM_Model
# import LlmModel
# from Run import GPTmodel

import re  
from sentence_transformers import SentenceTransformer, util
import numpy as np
import random  


class ExtractionAgent:
    def __init__(self, llmmodel):
        self.llmmodel = llmmodel  
        self.prompt_extract = """Role and Goal: 
You are an information extractor for identifying the tuples from the input text. Your goal is to extract and summarize a lists of tuples <SubjectEntity, ObjectEntity_1, ObjectEntity_2, MethodEntity_1, MethodEntity_2, ...> based on the input text to fully represent the essential semantics of the input text. Each tuple is a hierarchical tree-like unit containing only one SubjectEntity and one or more ObjectEntities and MethodEntities, depending on the length and semantics of the input text. Folllowing the provided instruction and example to generate the key-value pairs output in a JSON data structure format.

Instruction: 
The input text can be structured data (e.g., databases and data tables) or unstructured data (e.g., textual paragraphs). The tuples following the below instruction：
1. SubjectEntity: The main subjects that appear in the input text, serving as the primary descriptive objects of the text’s semantics; there can be multiple subjects, i.e., multiple tuples.
2. ObjectEntity: The properties or characteristics of the SubjectEntities.
3. MethodEntity: The executable functions or operations of the SubjectEntities. If it doesn't exist in input text, do not generate it.
4. Follow the "instruction" of Name, Definition, Data, and DataType in Example to fill the tuples.
5. DataType can be "Integer", "Double", "String", or "Boolean". 
6. Please output the response in JSON format only, without any additional text.
You need to determine how many tuples, ObjectEntities or MethodEntities in each tuple should be generated. And keep the key like "SubjectEntity_1", "ObjectEntity_1", or MethodEntity_1. Follow the structure and syntax as shown in the JSON file in the Example.

Example：
Input: // you will receive text in here
Output: 
{
    "tuples":[
        {"SubjectEntity_1": {
            "Name": "A concise and specific title for identifying the SubjectEntity_1",
            "Definition": "The concise definition for describing the SubjectEntity_1",
            "Type": "Object",
            "Children": [
                {"ObjectEntity_1":{
                      "Name": "A concise and specific title for identifying the ObjectEntity_1",
                      "Definition": "The definition for describing the ObjectEntity_1",
                      "Data": "The actual data that is described by the ObjectEntity_1",
                      "DataType": "The data type of the ObjectEntity_1's Data",
                      "Type": "Variable"
                    }
                },
                {"ObjectEntity_2":{
                      "Name": "A concise and specific title for identifying the ObjectEntity_2",
                      "Definition": "The definition for describing the ObjectEntity_2",
                      "Data": "The actual data that is described by the ObjectEntity_2",
                      "DataType": "The data type of the ObjectEntity_2's Data",
                      "Type": "Variable"
                    }
                },
                {"MethodEntity_1":{
                    "Name": "A concise and specific title for identifying the MethodEntity_1",
                    "Definition": "The definition for describing the MethodEntity_1",
                    "Type": "Method"
                    }
                }
            ]
          }
        }
    ] 
}

Input: // {{input_text}}

Output: 
"""

        status_logger.log("extraction agent is initialized")

    def generate_output(self, input_text, model):
        status_logger.log("extraction agent started analysis")
        self.prompt = self.prompt_extract.replace("{{input_text}}", input_text) 
        # print(self.prompt)

        # Get the text output from the GPT model call
        tuples_respond = self.llmmodel.llm_model_call(prompt=self.prompt,input_text="none",model=model) 
        
        print("tuples_respond = ", tuples_respond)
        # print("tuples_output = ", tuples_output)
        # print("usage = ", tuples_respond.usage)
        
        complete_response = ""  
        for chunk in tuples_respond:
            if chunk.choices and chunk.choices[0].delta.content is not None:
                print(chunk.choices[0].delta.content, end="")  
                complete_response += chunk.choices[0].delta.content  
        
        # Shaping if needed
        complete_response = re.search(r'{\s*"tuples":\s*\[.*\]\s*}', complete_response, re.DOTALL).group()   
        print(f"Reshape complete_response = {complete_response}\n")
        
        
        
        try:
            # Parse the text output into a JSON object
            # tuples_dict = json.loads(tuples_output.strip())  
            tuples_dict = json.loads(complete_response.strip())  
        except json.JSONDecodeError as json_err:
            # Handle JSON parsing errors
            status_logger.log(f"JSON decoding error: {json_err}")
            status_logger.log(f"Received text output: {complete_response}")
            return None

        # Write the JSON data to a file，
        with open('tuples_output.json', 'w') as file:
            json.dump(tuples_dict, file, indent=4)   
        status_logger.log("tuples extraction agent finished generation")
        status_logger.log(f"tuples extraction agent output: {tuples_dict}")
        return tuples_dict   
    
    def read_input_txt(self, pth):  
        with open(pth, 'r') as file:  
            self.input_text = file.read()  
            # print(self.input_text)  
        return self.input_text   
    
    def save_output_json(self, pth, out):
        # Write the JSON data to a file
        with open(pth, 'w') as file:
            json.dump(out, file, indent=4, 
                      ensure_ascii=False)   
        print("Save output of Extract Agent")
        # status_logger.log("tuples extraction agent finished generation")
        # status_logger.log(f"tuples extraction agent output: {tuples_dict}")
        


class EvaluateAgent:
    def __init__(self, llmmodel):
        self.llmmodel = llmmodel  
        self.prompt_evaluate = """Role and Goal: 
You are an evaluator for determining whether there are dissimilar ObjectEntities or MethodEntities in provided tuples_2 compared to provided tuples_1. Your goal is to populate the "Children" of the corresponding SubjectEntity in provided tuples_1 with the dissimilar ObjectEntities or MethodEntities from provided tuples_2, while maintaining the structure and syntax of provided tuples_1. Folllowing the provided instruction and example to generate the key-value pairs output in a JSON data structure format.

Instruction: 
You will receive the provided tuples_1 and tuples_2. The new tuples_1 following the below instruction:
1. You need to assess the similarity based on the "Name" and "Definition" of ObjectEntities or MethodEntities.
2. You need to traverse all ObjectEntities or MethodEntities in both provided tuples_1 and tuples_2, selecting the ObjectEntities or MethodEntities in provided tuples_2 that are different from those in provided tuples_1.
3. All information and structure of the dissimilar ObjectEntities or MethodEntities from provided tuples_2 should be directly integrated into provided tuples_1, while preserving the original structure, information, and syntax of provided tuples_1.
4. If there are no dissimilar ObjectEntities or MethodEntities, output tuples_1 directly.
You need to determine how many dissimilar ObjectEntities or MethodEntities need to be populated to tuples_1. Please output the response in JSON format only, without any additional text. Follow the structure and syntax as shown in the JSON file in the Example. 

Example:
Input: 
The provided tuples_1 is: // provided tuples_1
The provided tuples_2 is: // provided tuples_2
Output: 
{
    "tuples":[
        {"SubjectEntity_1": {
            "Name": "Copy Name of SubjectEntity_1 from provided tuples_1",
            "Definition": "Copy Definition of SubjectEntity_1 from provided tuples_1",
            "Type": "Object",
            "Children": [
                {"ObjectEntity_1":{
                      "Name": "Copy Name of ObjectEntity_1 from provided tuples_1",
                      "Definition": "Copy Definition of ObjectEntity_1 from provided tuples_1",
                      "Data": "Copy Data of ObjectEntity_1 from provided tuples_1",
                      "DataType": "Copy DataType of ObjectEntity_1 from provided tuples_1",
                      "Type": "Variable",
                    }
                },
                {"MethodEntity_1":{
                    "Name": "Copy Name of MethodEntity_1 from provided tuples_1",
                    "Definition": "Copy Definition of MethodEntity_1 from provided tuples_1",
                    "Type": "Method"
                    }
                }
                {"ObjectEntity_2":{
                      "Name": "Copy Name of dissimilar ObjectEntity_2 from provided tuples_2",
                      "Definition": "Copy Definition of dissimilar ObjectEntity_2 from provided tuples_2",
                      "Data": "Copy Data of dissimilar ObjectEntity_2 from provided tuples_2",
                      "DataType": "Copy DataType of dissimilar ObjectEntity_2 from provided tuples_2",
                      "Type": "Variable",
                    }
                },
                {"MethodEntity_2":{
                    "Name": "Copy Name of dissimilar MethodEntity_2 from provided tuples_2",
                    "Definition": "Copy Definition of dissimilar MethodEntity_2 from provided tuples_2",
                    "Type": "Method"
                    }
                }
            ]
          }
        }
    ] 
}

Input: 
The provided tuples_1 is: // {{tuples_1}}
The provided tuples_2 is: // {{tuples_2}}
Output: 
"""

        self.SenTransModel = SentenceTransformer("/remote-home/iot_wangrongkai/LLM-code/Text2UA-git/all-distilroberta-v1")

        status_logger.log("evaluate agent is initialized")

    def generate_output(self, input_tuple1, input_tuple2, model):
        status_logger.log("evaluate agent started analysis")
        
        self.prompt = self.prompt_evaluate.replace("{{tuples_1}}", json.dumps(input_tuple1)) \
                    .replace("{{tuples_2}}", json.dumps(input_tuple2))      
        # print(self.prompt)

        # Get the text output from the GPT model call
        CombTuple_respond = self.llmmodel.llm_model_call(prompt=self.prompt,input_text="none",model=model) 
        # tuples_output = tuples_respond.choices[0].message.content # respond里边的message的内容content输出
        
    

        complete_response = ""  
        for chunk in CombTuple_respond:
            if chunk.choices and chunk.choices[0].delta.content is not None:
                print(chunk.choices[0].delta.content, end="")   
                complete_response += chunk.choices[0].delta.content  
        
        # Shaping if needed
        complete_response = re.search(r'{\s*"tuples":\s*\[.*\]\s*}', complete_response, re.DOTALL).group()   
        # print(f"Reshape complete_response = {complete_response}\n")
        
        
        try:
            # Parse the text output into a JSON object
            # tuples_dict = json.loads(tuples_output.strip())  
            CombTuples_dict = json.loads(complete_response.strip())  
        except json.JSONDecodeError as json_err:
            # Handle JSON parsing errors
            status_logger.log(f"JSON decoding error: {json_err}")
            status_logger.log(f"Received text output: {complete_response}")
            return None

        sub_sentence_lst = []
        obj_method_sentence_lst = []
        """
        Check similarity
        """
        for sub in CombTuples_dict["tuples"]:   
            for key, value in sub.items():    
                if "Name" in value and "Definition" in value:
                    sen = value["Name"] + ": " + value["Definition"]
                    sub_sentence_lst.append(sen)
                if "Children" in value:
                    for ch_ele in value["Children"]:  
                        for obj, v in ch_ele.items(): 
                            if "Name" in v and "Data" in v:  # 此时是变量！
                                sen1 = v["Name"] + ": " + str(v["Data"])    
                                obj_method_sentence_lst.append(sen1)  
                            elif "Name" in v and "Data" not in v:  
                                sen1 = v["Name"]    
                                obj_method_sentence_lst.append(sen1) 
                            
        print(f"\n sub_sentence_lst = {sub_sentence_lst}, len = {len(sub_sentence_lst)} \n obj_method_sentence_lst = {obj_method_sentence_lst}, len = {len(obj_method_sentence_lst)} \n ")             
        
        
        Embedding_lst = self.SenTransModel.encode(obj_method_sentence_lst)  
        print(f'Embedding_lst={Embedding_lst}, len = {len(Embedding_lst)}')
        self.Embedding_lst = Embedding_lst   

        for sentence, embed in zip(obj_method_sentence_lst, Embedding_lst):
            # print(f'sentence = {sentence}')
            # print(f'embed = {embed}')
            print(f'each sentence embed len = {len(embed)}')   # embed len = 768

        # query_sen = "Load Capacity: The range of loads that the FANUC M-710IC can carry."
        # query_vec = self.SenTransModel.encode(query_sen)   
        

        score_lst = [[0 for j in range(len(Embedding_lst))] for i in range(len(Embedding_lst))]
        i,j = 0, 0
        
        for vec in Embedding_lst:
            j = 0 
            for vec1 in Embedding_lst:
                score = float(util.cos_sim(vec, vec1))   
                score_lst[i][j] = score
                j += 1
            i += 1
        print(f'score_lst = {score_lst}, shape = {np.array(score_lst).shape}')
        
        
        delete_id = find_delete_id(score_lst=score_lst, score_threshold=0.76)  
        print(f'delete_id = {delete_id}, shape = {np.array(delete_id).shape}')
        
        if len(delete_id) != 0:  
            new_id = [element for row in delete_id for element in row]  
    
            new_id.sort(reverse=True)

            for idx in new_id:
                all_keys = CombTuples_dict["tuples"][0].keys()  
                for key in all_keys:
                    del CombTuples_dict["tuples"][0][key]["Children"][idx] 
            
        final_tuples_dict = CombTuples_dict 

        json_string = json.dumps(final_tuples_dict, indent=4)  

        # Write the JSON data to a file
        with open('final_tuples_output.json', 'w') as file:
            file.write(json_string)  
            # json.dump(tuples_dict, file, indent=4)  
        status_logger.log("evaluate tuples agent finished generation")
        status_logger.log(f"evaluate tuples agent output: {json_string}")
        return final_tuples_dict   
    
    def read_input_json(self, pth):
    
        with open(pth, 'r') as file:  
            
            self.input_text = json.load(file)   
              
            # print(self.input_text)  
        return self.input_text       
    
    def save_output_json(self, pth, out):
        
        json_string = json.dumps(out, indent=4)  
        
        # Write the JSON data to a file
        with open(pth, 'w') as file:
            file.write(json_string)  
            # json.dump(out, file, indent=4, 
            #           ensure_ascii=False)  
        print("Save output of Evaluate Agent")
        # status_logger.log("tuples extraction agent finished generation")
        # status_logger.log(f"tuples extraction agent output: {tuples_dict}")
    
    def save_embeddings_list_npy(self, pth):
        
         np.save(pth, np.array(self.Embedding_lst))   
         print("Save embeddings list of Evaluate Agent in .npy")
        
    
    
class SchemaGenerateAgent:
    def __init__(self, llmmodel):
        
        self.llmmodel = llmmodel
        self.prompt_schema = """Role and Goal: 
You are an industrial automation domain expert for generating the schema of OPC UA information model about the input text. Your first goal is to document which objects and method nodes you believe would be necessary when establishing an OPC UA information model about the input text. All these nodes are used for generate shema. Then you need to generate a tree-structured schema that includes the MetaSubjectEntity, multiple SubjectEntities, and one or more MethodEntities. Where MetaSubjectEntity, SubjectEntities, and MethodEntities correspond to input text, objects nodes, and method nodes of your document, respectively. Folllowing the provided instruction and example to only generate the key-value pairs output in a JSON data structure format.

Instruction: 
The input text serve as a MetaObjectEntity. First, based on your domain knowledge, you should generate the necessary objects and method nodes for constructing OPC UA information model of the input MetaObjectEntity. The structure of schema is based on the OPC UA Information Model structure of document. The schema following the below instruction:
1. MetaSubjectEntity: The specific entity for constructing the OPC UA information model.
2. SubjectEntity: The objects nodes of document.
3. MethodEntity: The method nodes of document. The MethodEntity can exist in Children of any MetaSubjectEntity or SubjectEntity.
4. Name: A concise and specific title for identification.
5. Definition: The concise definition for describtion.
6. Type can be "Object" or "Method". 
7. Please do not replace the key like "MetaSubjectEntity", "SubjectEntity_1", or "MethodEntity_1".
8. Please directly output the scheme in a JSON data structure format based on your reasons, do not ask me questions!
You need to determine how many SubjectEntities and MethodEntities should be generated. Follow the structure and syntax as shown in the JSON file in the Example.

Example：
Input: The MetaSubjectEntity is // MetaSubjectEntity

Output:
{   
    "schema":{
        "MetaSubjectEntity": {
            "Name": "Name of MetaSubjectEntity",
            "Definition": "Definition of MetaSubjectEntity",
            "Type": "Object",
            "Children": [
                {"SubjectEntity_1":{
                    "Name": "Name of SubjectEntity_1",
                    "Definition": "Definition of SubjectEntity_1",
                    "Type": "Object",
                    "Children": [
                        {"MethodEntity_1":{
                            "Name": "Name of MethodEntity_1",
                            "Definition": "Definition of MethodEntity_1",
                            "Type": "Method"
                            }
                        }
                    ]
                    }
                },
                {"SubjectEntity_2":{
                        "Name": "Name of SubjectEntity_2",
                        "Definition": "Definition of SubjectEntity_2",
                        "Type": "Object",
                        "Children": [
                        {"MethodEntity_2":{
                            "Name": "Name of MethodEntity_2",
                            "Definition": "Definition of MethodEntity_2",
                            "Type": "Method"
                            }
                        }
                    ]
                    }
                },
                {"MethodEntity_3":{
                    "Name": "Name of MethodEntity_3",
                    "Definition": "Definition of MethodEntity_3",
                    "Type": "Method"
                    }
                }
            ]
        }
    }
}

Input: The MetaSubjectEntity is // {{MetaObjectEntity}}

Output:
"""
        status_logger.log("schema generate agent is initialized")

    def generate_output(self, input_text, model):
        status_logger.log("schema generate agent started analysis")
        self.prompt = self.prompt_schema.replace("{{MetaObjectEntity}}", input_text) 
        # print(self.prompt)

        # Get the text output from the GPT model call
        schema_respond = self.llmmodel.llm_model_call(prompt=self.prompt,input_text="none",model=model) 
        # schema_output = schema_respond.choices[0].message.content 
        
    
        complete_response = ""  
        for chunk in schema_respond:
            if chunk.choices and chunk.choices[0].delta.content is not None:
                print(chunk.choices[0].delta.content, end="") 
                complete_response += chunk.choices[0].delta.content  
                
        #  Shaping if needed
        complete_response = re.search(r'{\s*"schema":\s*{.*}\s*}', complete_response, re.DOTALL).group()   
        
        try:
            # Parse the text output into a JSON object
            # schema_dict = json.loads(schema_output.strip())  
            schema_dict = json.loads(complete_response.strip()) 
        except json.JSONDecodeError as json_err:
            # Handle JSON parsing errors
            status_logger.log(f"JSON decoding error: {json_err}")
            status_logger.log(f"Received text output: {complete_response}")
            return None

        # Write the JSON data to a file
        with open('schema_output.json', 'w') as file:
            json.dump(schema_dict, file, indent=4)   
        status_logger.log("schema generate agent finished generation")
        status_logger.log(f"schema generate agent output: {schema_dict}")
        return schema_dict   
    
    def read_input_txt(self, pth):
       
        with open(pth, 'r') as file:  
             
            self.input_text = file.read()  
            
            # print(self.input_text)  
        return self.input_text   
    
    def save_output_json(self, pth, out):
        # Write the JSON data to a file
        with open(pth, 'w') as file:
            json.dump(out, file, indent=4, 
                      ensure_ascii=False)  
        print("Save output of Schema Generate Agent")
        # status_logger.log("tuples extraction agent finished generation")
        # status_logger.log(f"tuples extraction agent output: {tuples_dict}")
        
        

class SyncReasonAgent:
    def __init__(self, llmmodel):
        
        self.llmmodel = llmmodel
        self.prompt_sync = """Role and Goal: 
You are an OPC UA senior modeling expert for determining the required variable nodes and method nodes when establishing an OPC UA information model based on the provided schema. 
Your goal is to iterate through all ObjectEntities and MethodEntities in provided tuples, consider the containment relationship between their "Definition" and the "Definition" of SubjectEntities in provided schema, determine which SubjectEntity each ObjectEntity or MethodEntity in provided tuples should be filled into, and provide reasons for your decision. Folllowing the provided instruction and example to generate the key-value pairs output in a JSON data structure format.

Instruction: 
You will receive the provided schema and provided tuples. The reasons following the below instruction:
1. You should iterate through all ObjectEntities and MethodEntities in provided tuples, determining which SubjectEntity these ObjectEntities or MethodEntities in provided tuples belong to and filling the results in "IsBelongTo".
2. These ObjectEntities or MethodEntities in provided tuples can belong to any MetaSubjectEntity or SubjectEntities in provided schema based on your reasons.
3. Please give reasons for your each decision in one or two sentence. And you need to add a key-value pair "Reason": "your reason here" to the corresponding ObjectEntities and MethodEntities. 
Please output the response in JSON format only, without any additional text. Follow the structure and syntax as shown in the JSON file in the Example. 

Example:
Input: 
The provided schema is: // provided schema
The provided tuples is: // provided tuples
Output: 
{   
    "reasons":[
        {"ObjectEntity_1":{
            "Name": "Copy Name of ObjectEntity_1 from provided tuples",
            "Definition": "Copy Definition of ObjectEntity_1 from provided tuples",
            "IsBelongTo":"Copy Name of SubjectEntity from provided schema",
            "Reason": "your reason here"
             }
        },
        {"ObjectEntity_2":{
            "Name": "Copy Name of ObjectEntity_2 from provided tuples",
            "Definition": "Copy Definition of ObjectEntity_2 from provided tuples",
            "IsBelongTo":"Copy Name of SubjectEntity from provided schema",
            "Reason": "your reason here"
             }
        },
        {"MethodEntity_1":{
            "Name": "Copy Name of MethodEntity_1 from provided tuples",
            "Definition": "Copy Definition of MethodEntity_1 from provided tuples",
            "IsBelongTo":"Copy Name of SubjectEntity from provided schema",
            "Reason": "your reason here"
            }
        },
        {"MethodEntity_2":{
            "Name": "Copy Name of MethodEntity_2 from provided tuples",
            "Definition": "Copy Definition of MethodEntity_2 from provided tuples",
            "IsBelongTo":"Copy Name of SubjectEntity from provided schema",
            "Reason": "your reason here"
            }
        }
    ]
}

Input: 
The provided schema is: // {{schema}}
The provided tuples is: // {{tuples}}
Output：
"""     
        self.prompt_sync_gpt = """Role and Goal: 
You are an OPC UA senior modeling expert for determining the required variable nodes and method nodes when establishing an OPC UA information model based on the provided schema. 
Your goal is to iterate through all ObjectEntities and MethodEntities in provided tuples, consider the containment relationship between their "Definition" and the "Definition" of SubjectEntities in provided schema, determine which SubjectEntity each ObjectEntity or MethodEntity in provided tuples should be filled into, and provide reasons for your decision. Folllowing the provided instruction and example to generate the key-value pairs output in a JSON data structure format.

Instruction: 
You will receive the provided schema and provided tuples. The reasons following the below instruction:
1. You should iterate through all ObjectEntities and MethodEntities in provided tuples, determining which SubjectEntity these ObjectEntities or MethodEntities in provided tuples belong to and filling the results in "IsBelongTo".
2. These ObjectEntities or MethodEntities in provided tuples can belong to any MetaSubjectEntity or SubjectEntities in provided schema based on your reasons.
3. Please give reasons for your each decision in one or two sentence. And you need to add a key-value pair "Reason": "your reason here" to the corresponding ObjectEntities and MethodEntities. 
You need to determine how many traversed ObjectEntities or MethodEntities should be generated. Please output the response in JSON format only, without any additional text. Follow the structure and syntax as shown in the JSON file in the Example. 

Example:
Input: 
The provided schema is: // provided schema
The provided tuples is: // provided tuples
Output: 
{   
    "reasons":[
        {"ObjectEntity from provided tuples":{
            "Name": "Copy Name of ObjectEntity from provided tuples",
            "Definition": "Copy Definition of ObjectEntity from provided tuples",
            "IsBelongTo":"Copy Name of SubjectEntity from provided schema",
            "Reason": "your reason here"
             }
        },
        {"MethodEntity from provided tuples":{
            "Name": "Copy Name of MethodEntity_1 from provided tuples",
            "Definition": "Copy Definition of MethodEntity_1 from provided tuples",
            "IsBelongTo":"Copy Name of SubjectEntity from provided schema",
            "Reason": "your reason here"
            }
        }
    ]
}

Input: 
The provided schema is: // {{schema}}
The provided tuples is: // {{tuples}}
Output：
"""  

        self.reasons = {} 
        status_logger.log("sync reason agent is initialized")

    def generate_output(self, input_schema, input_tuples, model):
        status_logger.log("sync reason agent started analysis")
        
        if model in ['gpt-3.5-turbo-instruct']:
            self.prompt = self.prompt_sync_gpt.replace("{{schema}}", json.dumps(input_schema)) \
                    .replace("{{tuples}}", json.dumps(input_tuples))  
        elif model in ['llama-3.1-405b-instruct']:
            self.prompt = self.prompt_sync.replace("{{schema}}", json.dumps(input_schema)) \
                        .replace("{{tuples}}", json.dumps(input_tuples))  
        else:
            self.prompt = self.prompt_sync.replace("{{schema}}", json.dumps(input_schema)) \
                    .replace("{{tuples}}", json.dumps(input_tuples))           
        
        # print(self.prompt)
        

        # Get the text output from the GPT model call
        sync_respond = self.llmmodel.llm_model_call(prompt=self.prompt,input_text="none",model=model) 
        # schema_output = schema_respond.choices[0].message.content # respond里边的message的内容content输出
        
     
        complete_response = ""  
        for chunk in sync_respond:
            if chunk.choices and chunk.choices[0].delta.content is not None:
                print(chunk.choices[0].delta.content, end="") 
                complete_response += chunk.choices[0].delta.content  
        
        
       
        complete_response = re.search(r'{\s*"reasons":\s*\[.*?\]\s*}', complete_response, re.DOTALL).group()  
        
        
        
        try:
            # Parse the text output into a JSON object
            # schema_dict = json.loads(schema_output.strip())  
            reason_dict = json.loads(complete_response.strip())  
            self.reasons = reason_dict   
        except json.JSONDecodeError as json_err:
            # Handle JSON parsing errors
            status_logger.log(f"JSON decoding error: {json_err}")
            status_logger.log(f"Received text output: {complete_response}")
            return None
        
        """Follow reason_dic to combine input_schema and input_tuples
        """
        target_id_lst = []  
        source_id_lst = []  
        reasons_lst = [] 
        for obj in reason_dict["reasons"]: 
            # print(obj)  
            for key, value in obj.items():   
                # print(key)
                # print(value)
                if "IsBelongTo" in value:  
                    # print(value["IsBelongTo"])  
                    target_id = value["IsBelongTo"]
                    target_id_lst.append(target_id)
                if "Name" in value:  
                    # print(value["Name"])  
                    source_id = value["Name"]
                    source_id_lst.append(source_id)
                if "Reason" in value:  
                    # print(value["Name"])  
                    reason_id = value["Reason"]
                    reasons_lst.append(reason_id)
        print(f"\ntarget_id_lst = {target_id_lst} \n source_id_lst = {source_id_lst} \n reasons_lst = {reasons_lst} \n")

        # target_dict = copy.deepcopy(target_data)  
        object_entity_lst = []
        desc = ""
        for lst_ele in input_tuples["tuples"]:
            # print(lst_ele) 
            for key, value in lst_ele.items():   
                desc = value["Definition"]
                if "Children" in value:
                    for children_ele in value["Children"]: 
                        for k1, v1 in children_ele.items():  
                            if "Name" in v1: 
                                for sour in source_id_lst:
                                    if sour == v1["Name"]: 
                                        object_entity = children_ele  
                                        object_entity_lst.append(object_entity)
                        
                                        # source_id_lst.remove(sour)  
                                        break 
        print(f"object_entity_lst = {object_entity_lst}, len = {len(object_entity_lst)} \n")  
        # print(f"object_entity_lst[1] = {object_entity_lst[1]} \n") 
        
        i = 0  
        for ele in object_entity_lst:  
            print(ele)
            for k, v in ele.items(): 
                v['Reason'] = reasons_lst[i]  
                i += 1 
                print(i,v)
        print(f"Add reason：object_entity_lst = {object_entity_lst} \n") 

                      
        for ele in input_schema["schema"]["MetaSubjectEntity"]["Children"]:    
            # print(ele)
            for key, value in ele.items(): 
                # print(key, value)
                if "Name" in value:  
                    index_of_tar = 0 
                    for tar in target_id_lst: 
                        # print(tar)
                        # print(index_of_tar)
                        if tar == value["Name"]:
                            if index_of_tar < len(object_entity_lst):
                                value["Children"].append(object_entity_lst[index_of_tar])  
                            index_of_tar += 1
                        else:
                            index_of_tar += 1
    
        index_of_tar = 0  
        for tar in target_id_lst: 
            if tar == input_schema["schema"]["MetaSubjectEntity"]["Name"]:
                input_schema["schema"]["MetaSubjectEntity"]["Children"].append(object_entity_lst[index_of_tar])  
                index_of_tar += 1
            else:
                index_of_tar += 1
        
        input_schema["schema"]["MetaSubjectEntity"]["Definition"] += f". {desc}" 
        print(f"Reshape: input_schema = {input_schema} \n")  
        
       
        json_string = json.dumps(input_schema, indent=4) 

        # Write the JSON data to a file
        with open('sync_output.json', 'w') as file:
            file.write(json_string)  
        status_logger.log("schema generate agent finished generation")
        status_logger.log(f"schema generate agent output: {json_string}")
        return input_schema   
    
    def read_input_json(self, pth):
         
        with open(pth, 'r') as file:  
             
            self.input_text = json.load(file)  
            # print(self.input_text)  
        return self.input_text     
    
    def save_output_json(self, pth, out):
        
        json_string = json.dumps(out, indent=4)  
        # Write the JSON data to a file
        with open(pth, 'w') as file:
            file.write(json_string)  
            
        print("Save output of Sync Reason Agent")
        # status_logger.log("tuples extraction agent finished generation")
        # status_logger.log(f"tuples extraction agent output: {tuples_dict}")
    
    def save_reason_json(self, pth, out=None):  
        if out is None:  
            out = self.reasons  
        
        # Write the JSON data to a file
        with open(pth, 'w') as file:
            json.dump(out, file, indent=4, 
                      ensure_ascii=False)   
        print("Save reasons output of Sync Reason Agent")
        
    
class TransformAgent:
    def __init__(self, llmmodel):
        
        self.llmmodel = llmmodel
        self.prompt_trans = """Role and Goal: 
You are a data conversion expert fot converting data from JSON format to XML format. Your goal is to traverse all the key-value pairs in provided JSON text, following the conversion rules in provided instruction and example to sequentially generate the corresponding text in a XML data structure format.  

Instruction: 
You will receive the provided JSON text. The generated XML following the below instruction:
1. The MetaSubjectEntity, SubjectEntity, ObjectEntity, and MethodEntity in provided JSON are converted to ObjectType, Object, Property, and Method elements in generated XML, respectively.
2. The value of "Name", "Definition", "Data", "Datatype" in provided JSON are filled into the content text of SymbolicName, Description, DefaultValue, and DataType elements in generated XML, respectively.
3. Please generate corresponding XML elements according to the original data structure in procided JSON, while adhering to the structure and syntax of XML.
4. Please do not replace the the text like "OPCUAbyLLM", "ua", or "uax".
5. Please output the response in XML format only, without any additional text.
Follow the structure and syntax as shown in the XML file in the Example.

Example:
Input: The provided JSON text is: // provided JSON text

Output:
<ObjectType BaseType="ua:BaseObjectType" SupportsEvents="true" SymbolicName="OPCUAbyLLM:Name of object_1">
<Description>Definition of object_1</Description>
<Children>
    <Property DataType="ua:DataType of variable_1" ModellingRule="Mandatory" SymbolicName="OPCUAbyLLM:Name of variable_1" ValueRank="Scalar"> 
        <Description>Definition of variable_1</Description>
        <DefaultValue>
            <uax:DataType of variable_1>Data of variable_1</uax:DataType of variable_1>
        </DefaultValue> 
    </Property> 
    <Method SymbolicName="OPCUAbyLLM:Name of method_1">
        <Description>Definition of method_1</Description>
    </Method> 
    <Object ModellingRule="Mandatory" SymbolicName="OPCUAbyLLM:Name of object_2">
        <Children>
            <Property DataType="ua:DataType of variable_2" ModellingRule="Mandatory" SymbolicName="OPCUAbyLLM:Name of variable_2" ValueRank="Scalar">
                <Description>Definition of variable_2</Description> 
                <DefaultValue>
                    <uax:DataType of variable_2>Data of variable_2</uax:DataType of variable_2>
                </DefaultValue> 
            </Property>
            <Method SymbolicName="OPCUAbyLLM:Name of method_2">
                <Description>Definition of method_2</Description>
            </Method>   
        </Children>
    </Object>
</Children>
</ObjectType>

Input: The provided JSON text is: // {{json_text}}

Output:
"""
        status_logger.log("transform agent is initialized")

    def generate_output(self, input_json, model):
        status_logger.log("transform started analysis")
        
        # # read the JSON data to a python dict...
        # with open('sync_output.json', 'r') as file:
        #     input_json = json.load(file)  
        
        self.prompt = self.prompt_trans.replace("{{json_text}}", json.dumps(input_json))  
        # print(self.prompt)
        

        # Get the text output from the GPT model call
        xml_respond = self.llmmodel.llm_model_call(prompt=self.prompt,input_text="none",model=model) 
        
        complete_response = ""  
        for chunk in xml_respond:
            if chunk.choices and chunk.choices[0].delta.content is not None:
                print(chunk.choices[0].delta.content, end="") 
                complete_response += chunk.choices[0].delta.content  
                
        #  Shaping if needed
        complete_response = re.search(r'<ObjectType[^>]*>.*?</ObjectType>', complete_response, re.DOTALL).group() 
                
        xml_head = """<ModelDesign xmlns="http://opcfoundation.org/UA/ModelDesign.xsd" xmlns:OPCUAbyLLM="https://opcua.WRK/UA/OPCUAbyLLM/" xmlns:ua="http://opcfoundation.org/UA/" xmlns:uax="http://opcfoundation.org/UA/2008/02/Types.xsd" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" TargetNamespace="https://opcua.WRK/UA/OPCUAbyLLM/" TargetPublicationDate="2024-08-16T00:00:08Z" TargetVersion="1.0.0" TargetXmlNamespace="https://opcua.WRK/UA/OPCUAbyLLM/">
<Namespaces>
<Namespace Name="OPCUAbyLLM" Prefix="OPCUAbyLLM" XmlNamespace="https://opcua.WRK/UA/OPCUAbyLLM/Types.xsd" XmlPrefix="OPCUAbyLLM">https://opcua.WRK/UA/OPCUAbyLLM/</Namespace>
<Namespace InternalPrefix="Opc.Ua.Server" Name="OpcUa" Prefix="Opc.Ua" PublicationDate="2013-12-02T00:00:00Z" Version="1.03" XmlNamespace="http://opcfoundation.org/UA/2008/02/Types.xsd" XmlPrefix="OpcUa">http://opcfoundation.org/UA/</Namespace>
</Namespaces>
{{xml_out}}
</ModelDesign>
        """
        
        xml_text = xml_head.replace("{{xml_out}}", complete_response)   
        
        #  validate and change  
        modified_xml = re.sub(r'SymbolicName="([^"]*)"', lambda x: 'SymbolicName="' + x.group(1).replace(' ', '_') + '"', xml_text)  
        
        # uax:Integer --  uax:UInt64  
        modified_xml = modified_xml.replace('uax:Integer', 'uax:UInt64') 
        modified_xml = modified_xml.replace('ua:Integer', 'ua:UInt64') 
        # OPCUAbyLLM: --  OPCUAbyLLM:_
        modified_xml = modified_xml.replace('OPCUAbyLLM:', 'OPCUAbyLLM:_')  
        

        # Write the JSON data to a file，
        with open('xml_output.xml', 'w') as file:
            file.write(modified_xml)  
        status_logger.log("tranform agent finished generation")
        status_logger.log(f"transform agent output: {modified_xml}")
        return modified_xml  
    
    def read_input_json(self, pth):
        
        with open(pth, 'r') as file:  
            
            self.input_text = json.load(file) 
            
            # print(self.input_text)  
        return self.input_text     
    
    def save_output_xml(self, pth, out):
        # Write the JSON data to a file
        with open(pth, 'w') as file:
            file.write(out)   
        print("Save output of Tansform Agent")
        # status_logger.log("tuples extraction agent finished generation")
        # status_logger.log(f"tuples extraction agent output: {tuples_dict}")





def find_delete_id(score_lst, score_threshold=0.8):
    
    score_array = np.array(score_lst)  
    
    indices = np.argwhere(score_array > score_threshold)   
    # print(indices)
    
    sorted_indices = np.sort(indices, axis=1)  
    unique_indices = np.unique(sorted_indices, axis=0)  
    # print(unique_indices)  

    id_lst_repeat = unique_indices.tolist() 
    print(f"id_lst_repeat={id_lst_repeat}") 
    
 
    id_lst = [x for x in id_lst_repeat if len(set(x)) > 1]  
    print(f"id_lst={id_lst}") 

    if len(id_lst) != 0:   
        
        # print(result)
        
        # input_list = [[0, 1], [0, 3],[2, 4], [0, 5], [2, 4]]  
        result = []  
        change_result = []
        temp = id_lst[0] # 47
        # print(temp)   
        i = 0
        for sublist in id_lst:  
            # print(sublist)  47  48 69 78
            for num in sublist:  # 4  7
                # print(num)
                if len(result)!=0: 
                    
                    # pass
                    change_result = result  
                    
                    # for lst in result:
                    for j in range(len(result)):
                        if num in result[j]:  
                            change_result[j].extend(sublist) # 47 47 48
                            # print(temp)
                            i = 0
                            break  
                        else:
                            i += 1
                    print(f'change_result={change_result}')
                    
                    if i == 2*(len(result)):  
                        # list1 = temp
                        # print(list1)
                        change_result.append(sublist)  # 47 47 48 ， 69， 78
                        # print(result)
                        # temp = sublist 
                        # print(temp)
                        i = 0
                    
                    # result = change_result
                    
                else:  
                    if num in temp:  
                        temp.extend(sublist) 
                        # print(temp)
                        i=0
                        break  
                    else:
                        i += 1
                    if i == 2: 
                        # list1 = temp 
                        # print(list1)
                        result.append(temp)  # 47 47 48 ， 69， 78
                        result.append(sublist)  
                        print(f'result={result}')
                        # print(result)
                        # temp = sublist  
                        # print(temp)
                        i = 0
            result = change_result
        if len(result)==0:    
            result.append(temp)  
        
        print(f'final- result={result}')
        
        delet_id = []
        for lst in result:
            list2 = list(set(lst))   
            random_number = random.choice(list2)  
            list2.remove(random_number) 
            delet_id.append(list2) 
    else:
        delet_id = []
 
    # print(delet_id)
    return delet_id   


