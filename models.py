from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate,ChatMessagePromptTemplate
from langchain_core.runnables import RunnablePassthrough,RunnableParallel
from langchain_community.document_loaders import TextLoader,Docx2txtLoader

import tempfile
import streamlit as st

from dotenv import load_dotenv
import os

load_dotenv()

class AnswerGenerator:
    def __init__(self):
        self.model = ChatGroq(
            model_name="llama-3.3-70b-versatile",
            temperature=0.7,
            api_key=os.getenv("GROQ_API_KEY")
        )
        self.temp_path = None
        self.jd_documents = []
        self.resume_documents = []
    
    def save_to_temp(self,uploaded_file):
        suffix = os.path.splitext(uploaded_file.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.read())
            self.temp_path = tmp.name
        
    
    def clean_up(self):
        if self.temp_path and os.path.exists(self.temp_path):
            os.remove(self.temp_path)
            self.temp_path = None
    
    def jd_loader(self,jd_file):
        try:
            self.save_to_temp(jd_file)
            if not self.temp_path:
                raise ValueError("Temporary file not created yet.")
            loader = TextLoader(self.temp_path,  encoding="utf-8")
            document = loader.load()
            self.jd_documents = document[0].page_content
            return self.jd_documents
            st.error(e)
        finally:
            self.clean_up()
        
    def resume_loader(self,resume_file):
        try:
            self.save_to_temp(resume_file)
            if not self.temp_path:
                raise ValueError("Temporary file not created yet.")
            loader = Docx2txtLoader(self.temp_path)
            document = loader.load()
            self.resume_documents = document[0].page_content
            return self.resume_documents
            st.error(e)
        finally:
            self.clean_up()
        
