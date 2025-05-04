from doc_loader import DocumnetLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
import streamlit as st



class VectorStore:
    MODEL_PATH = "./models/all-MiniLM-l6-v2/"
    DEVICE = "cpu"
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    def __init__(self):
        """Initialize embedding model for vector store."""
        try:
            self.embedding = HuggingFaceEmbeddings(
                model_name=self.MODEL_PATH,
                model_kwargs={"device": self.DEVICE},
                encode_kwargs={"normalize_embeddings": False}
            )
        except Exception as e:
            st.error(f"Embedding model initialization failed: {e}")
            
    
    def text_splitter(self, document):
        '''Splitting the Document into Chunks'''
        try:
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.CHUNK_SIZE,
                chunk_overlap=self.CHUNK_OVERLAP,
                length_function=len
            )
            return splitter.split_documents(document)
            
        except Exception as e:
            st.error(e)
            
    def vector_store(self, document):
        try:
            chunks  = self.text_splitter(document=document)
            return FAISS.from_documents(chunks, self.embedding)
        except Exception as e:
            st.error(e)