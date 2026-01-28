# LLM Probing for Polysemy Understanding

This repository contains code and materials for investigating
the semantic understanding of large language models (LLMs) through probing tasks.

The project examines how different models handle polysemous words in Chinese,
with probing questions designed to target distinct components of semantic cognition,
including protoscene recognition, subtle sense distinction, and sense relation identification.


## Project Overview
The study evaluates:
- Generative LLMs (e.g., GPT-3.5, DeepSeek)
- An encoder-based baseline (BERT)

Models are tested on probing tasks derived from linguistic and cognitive theories of polysemy,
and their responses are compared with human judgments from native speakers.

## Repository Structure
```

├── metadata/ # Labels of the four polysemes and their senses
├── pipeline/
│ ├── retrieve_sentence/ # Retrieve example sentences from Bing API
│ ├── generators/ # Generate different types of probing questions
│ ├── question_generation/ # Generate questions, assign gold options, and shuffle order
│ ├── run_models/ # Prompt LLMs and collect responses
│ └── analysis/ # Statistical evaluation of model outputs
└── README.md
```
