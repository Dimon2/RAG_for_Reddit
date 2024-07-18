from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters.character import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

import json
import os
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

current_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(current_dir, "text_data")
Path(data_path).mkdir(parents=True, exist_ok=True)
persistent_directory = os.path.join(current_dir, "db", "chroma_db")
Path(persistent_directory).mkdir(parents=True, exist_ok=True)

if not os.path.exists(persistent_directory):
    print("Persistent directory does not exist. Initializing vector store...")

    if not os.path.exists(data_path):
        raise FileNotFoundError(f"The directory {data_path} does not exist")
    
    text_data = {}
    for file_name in os.listdir(data_path):        
        file_path = os.path.join(data_path, file_name)
        if not os.path.isfile(file_path): continue
        loader = TextLoader(file_path)        
        text_data = loader.load()
        for doc in text_data:
            json_data = json.loads(doc.page_content)
            comments = []
            for comment in json_data["comments"]:
                comments.append(comment["text"])
                comments.extend(reply for reply in comment.get("replies", []))
            doc.page_content = "\n".join([json_data["text"]] + comments)
            doc.metadata = json_data["metadata"]

  
    text_spliter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200, separator='\n')
    chunk_data = text_spliter.split_documents(text_data)
       
    print(f"Number of document chunks: {len(chunk_data)}")

    print("Creating embedding")

    model_name = "sentence-transformers/all-mpnet-base-v2"
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': False}
    embedding = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )
    print("Embedding created")
    db = Chroma.from_documents(chunk_data, embedding, persist_directory=persistent_directory)
    print("\n Finished creating vector store")
else:
    print("Database is already exists. No need to initialize")


