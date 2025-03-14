# Text2UA
Official implementation for "Text2UA: Automatic OPC UA Information Modeling from Textual Data with Large Language Model" (JAS-2024). 

# Text2UA (Automated OPC UA Information Modeling from Text)
> [**JAS-24**] [**Text2UA: Automatic OPC UA Information Modeling from Textual Data with Large Language Model**](https://www.ieee-jas.net/en/article/doi/10.1109/JAS.2025.125114)
>
> by [Rongkai Wang](https://scholar.google.com.hk/citations?hl=zh-CN&user=l-zF-W0AAAAJ),  [Chaojie Gu](https://scholar.google.com.hk/citations?hl=zh-CN&user=P7O3FpsAAAAJ), [Shibo He](https://scholar.google.com/citations?hl=zh-CN&user=5GOcb4gAAAAJ&view_op=list_works&sortby=pubdate), [Jiming Chen](https://scholar.google.com/citations?user=zK9tvo8AAAAJ&hl=zh-CN).


## Updates

- **12.12.2024**: Accept! Code is coming soon !!!
- **03.03.2025**：Early Access！

## Introduction 
We deals with automatically constructing an OPC UA information model (IM) aimed at enhancing data interoperability among heterogeneous system components within manufacturing automation systems. Empowered by the large language model (LLM), we propose a novel multi-agent collaborative framework to streamline the endto-end OPC UA IM modeling process. Each agent is equipped with meticulously engineered prompt templates, augmenting their capacity to execute specific tasks. We conduct modeling experiments using real textual data to demonstrate the effectiveness of the proposed method, improving modeling efficiency and reducing the labor workload.

- *End-to-end efficient OPC UA information modeling method*
- *Compatible with multiple data sources*
- *Do not rely on a predefined reference data model*

## Motivation（Easy Build for OPC UA Information Modeling）
<img src="./Assets/motivation.png" width="800" alt="Motivation">

Data sources are divided into structured data (STD) and unstructured data (NSTD), utilized for describing device properties, production resource status, task requirements, etc. Modeling occurs in two scenarios:
1) **Known system components:** these components are currently in use and have generated data (e.g., STD: sheets or tables) representing their key properties or the system’s requirements. These data are represented through various structured pairs composed of text and their corresponding values (TVPs). In such cases, the IM can be directly modeled based on these TVPs.
2) **Unknown system components** (e.g., newly accessed devices): these components have not yet been put into use and require a survey or understanding of their properties or functions based on technical documents or specifications (i.e., NSTD). In this scenario, we need to extract useful information from relevant texts and create a reference template for OPC UA IM. 

**Existing Limitation:**
1) Manually identifying and summarizing the information needed for modeling from data sources is a labor-intensive modeling method with low efficiency.
2) Mapping rule-based modeling methods require a reference data model established through prior manual efforts and are difficult to adapt to dynamic changes. 


## Table2UA(Using RDB to quickly construct OPC UA IM)
<!-- ![System architecture](./Assets/xxx.png) -->
<img src="./Assets/xxx.png" width="800" alt="System architecture">

## Overview of Multi-Agent Collabrative Modeling Framework
![Overview](./Assets/xxx.png)

## Promp Engineering Template
<img src="./Assets/xxx.png" width="600" alt="System model">

### Industrial dataset
![industrial](./assets/Industrial.png) 


## Main results
![Main result1](./Assets/table1.png) 
![Main result2](./Assets/table2.png) 
![Main result3](./Assets/table3.png) 


## How to Run
### Generate the dataset 
Generate the dataset below:
Take xxxxx for example

Structure of xxx Folder:
```
xxx/
│
├── xxx
│   
└── ...
```

```bash
cd xxxx
python xxxx.py
```

### Run E2E-MAPPO
* Quick start 
```bash
xxxxxx
```
  
* Train your own model
```bash
xxxxxxxx
```


## Main results ()

## Dataset
<img src="./Assets/xxx.png" width="600" alt="System model">

## We provide the reproduction of  [here]() 


<!-- * We re-program the DRL environment for multi-rewards feedback and single-step selection for FJSP.-->
* We thank for the code repository: [xxxx](xxxx)


## BibTex Citation

If you find this paper and repository useful, please cite our paper.

```
@articleInfo{JAS-2024-1271,
title = "Text2UA: Automatic OPC UA Information Modeling from Textual Data with Large Language Model",
journal = "IEEE/CAA Journal of Automatica Sinica",
volume = "12",
number = "JAS-2024-1271,
pages = "1",
year = "2025",
note = "",
issn = "2329-9266",
doi = "10.1109/JAS.2025.125114",
url = "https://www.ieee-jas.net/en/article/doi/10.1109/JAS.2025.125114",
author = "Rongkai Wang","Chaojie Gu","Shibo He","Jiming Chen"
}
```
