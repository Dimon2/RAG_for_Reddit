# LangChain Chatbot

## Introduction

LangChain Chatbot is a Python-based chatbot that interacts with an LLM (Language Model) and searches for answers in scrapped data from Reddit. It consists of three main components:

1. create_text_data.py: This script collects comments from Reddit and stores them in local files. You can use it to gather text data for training or testing your chatbot.
2. create_chromadb.py: The Chroma database creation script. Chroma is an open-source embedding database that allows you to build Python or JavaScript LLM apps with memory.
3. rag.py: This file is related to Retrieval Augmented Generation (RAG). RAG integrates retrieval into the sequence generation process, enhancing contextually appropriate responses by fetching relevant documents based on a query.

## Installation

```
pip install -r requirements.txt
```

## Usage

1. Install **pip install -r requirements.txt**
2. Fill your **.env** file with your data.
3. Run **create_text_data.py** to scrape comments from Reddit. Adjust the subreddit or other parameters as needed. The default subreddits are specified in the **crawler.py** file (stocks, investing, stockmarket, wallstreetbets).
4. To create the Chroma Database, execute **create_chromadb.py**.
5. To run the chatbot, use **rag.py**. The chatbot will interact with an LLM and retrieve relevant information from the Chroma database.
