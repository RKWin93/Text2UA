# Text2UA
Official implementation for "Text2UA: Automatic OPC UA Information Modeling from Textual Data with Large Language Model" (JAS-2024). 

# Text2UA (Automatied OPC UA Information Modeling from Text)
> [**JAS-24**] [**Text2UA: Automatic OPC UA Information Modeling from Textual Data with Large Language Model**](https://www.ieee-jas.net/en/article/doi/10.1109/JAS.2025.125114)
>
> by [Rongkai Wang](https://scholar.google.com.hk/citations?hl=zh-CN&user=l-zF-W0AAAAJ),  [Chaojie Gu](https://scholar.google.com.hk/citations?hl=zh-CN&user=P7O3FpsAAAAJ), [Shibo He](https://scholar.google.com/citations?hl=zh-CN&user=5GOcb4gAAAAJ&view_op=list_works&sortby=pubdate), [Jiming Chen](https://scholar.google.com/citations?user=zK9tvo8AAAAJ&hl=zh-CN).


## Updates

- **12.12.2024**: Accept! Code is coming soon !!!
- **03.03.2025**：Early Access！

## Introduction 
We deals with automatically constructing an OPC UA information model (IM) aimed at enhancing data interoperability among heterogeneous system components within manufacturing automation systems. Empowered by the large language model (LLM), we propose a novel multi-agent collaborative framework to streamline the endto-end OPC UA IM modeling process. Each agent is equipped with meticulously engineered prompt templates, augmenting their capacity to execute specific tasks. We conduct modeling experiments using real textual data to demonstrate the effectiveness of the proposed method, improving modeling efficiency and reducing the labor workload.

## Motivation and Table2UA(Using RDB to construct OPC UA IM)
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
