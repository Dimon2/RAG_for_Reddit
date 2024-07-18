from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEndpoint
from langchain.chains.combine_documents.stuff import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain_core.prompts.chat import ChatPromptTemplate, MessagesPlaceholder

import os

current_dir = os.path.dirname(os.path.abspath(__file__))
persistent_directory = os.path.join(current_dir, "db", "chroma_db")

model_name = "sentence-transformers/all-mpnet-base-v2"
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': False}
embedding = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)

db = Chroma(embedding_function=embedding, persist_directory=persistent_directory)
retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 3})

llm = HuggingFaceEndpoint(
    repo_id="mistralai/Mistral-7B-Instruct-v0.2",
    task="text-generation",
    max_new_tokens=512,
    do_sample=False,
    repetition_penalty=1.03,
)

contextualize_q_system_prompt = (
    "Given a chat history and the latest user question"
    "which might reference context in the chat history," 
    "formulate a standalone question" 
    "which can be understood without the chat history. Do NOT answer the question," 
    "just reformulate it if needed and otherwise return it as is."
)

contextualize_q_prompt = ChatPromptTemplate.from_messages([
    ("system",  contextualize_q_system_prompt),
    MessagesPlaceholder("chat_history"),
    ("user",  "{input}")
])

history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)

qa_system_prompt = (
    "You are assistant for question-answering tasks."
    "Use the following piece of information to answer the question."
    "If you don't know the answers to the user questions, truthfully say you don't know."
    "\n\n"
    "{context}"
)

qa_prompt = ChatPromptTemplate.from_messages([
    ("system", qa_system_prompt),
    MessagesPlaceholder("chat_history"),
    ("user", "{input}")
])

question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

def continual_chat():
    chat_history = []

    while True:
        query = input("You: ")
        if query.lower() == "exit":
            break
        result = rag_chain.invoke({"input" : query, "chat_history": chat_history})

        print(f"AI: {result['answer']}")
        chat_history.append({"role": "user", "content": query})
        chat_history.append({"role": "system", "content": result['answer']})

if __name__ == "__main__":
    continual_chat()

