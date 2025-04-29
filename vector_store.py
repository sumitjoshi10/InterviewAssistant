from doc_loader import DocumnetLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
import streamlit as st


class VectorStore:
    def __init__(self):
        '''Creating the Vector Store using the FAISS'''
        self.model_name = "./models/all-MiniLM-l6-v2/"
        self.model_kwargs = {'device': 'cpu'}
        self.encode_kwargs = {'normalize_embeddings': False}
        self.embedding = HuggingFaceEmbeddings(
            model_name=self.model_name,
            model_kwargs=self.model_kwargs,
            encode_kwargs=self.encode_kwargs
        )
    
    def text_splitter(self, document):
        '''Splitting the Document into Chunks'''
        try:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=100,
                length_function=len
            )
            chunks = text_splitter.split_documents(document)
            return chunks
        except Exception as e:
            st.error(e)
            
    def vector_store(self, document):
        chunks  = self.text_splitter(document=document)
        vector_store  = FAISS.from_documents(chunks, self.embedding)
        return vector_store