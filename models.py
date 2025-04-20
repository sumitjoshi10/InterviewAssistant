from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate,ChatMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser,PydanticOutputParser
from langchain_core.runnables import RunnablePassthrough,RunnableParallel
from langchain_community.document_loaders import TextLoader,Docx2txtLoader

import tempfile
import streamlit as st
from pydantic import BaseModel, Field
from typing import Literal

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
    
    def _save_to_temp(self,uploaded_file):
        '''Saving to the Temporary File Resume and JD Uploaded File'''
        suffix = os.path.splitext(uploaded_file.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.read())
            self.temp_path = tmp.name
          
    def _clean_up(self):
        '''Cleaning Up the Temp File after Conversion'''
        if self.temp_path and os.path.exists(self.temp_path):
            os.remove(self.temp_path)
            self.temp_path = None
    
    def jd_loader(self,jd_file):
        '''Loading the JD file and reading the page content'''
        try:
            self._save_to_temp(jd_file)
            if not self.temp_path:
                raise ValueError("Temporary file not created yet.")
            loader = TextLoader(self.temp_path,  encoding="utf-8")
            document = loader.load()
            self._jd_summarizer(document[0].page_content)
            return self.jd_documents   ### to check whether it is generating the response
        except Exception as e:
            st.error(e)
        finally:
            self._clean_up()
        
    def resume_loader(self,resume_file):
        '''Loading the Resume File  and reading the Document'''
        try:
            self._save_to_temp(resume_file)
            if not self.temp_path:
                raise ValueError("Temporary file not created yet.")
            loader = Docx2txtLoader(self.temp_path)
            document = loader.load()
            self.resume_documents = document[0].page_content
            return self.resume_documents ### to check whether it is generating the response
        except Exception as e:
            st.error(e)
        finally:
            self._clean_up()
            
    def _jd_summarizer(self, document):
        prompt_summarizer = PromptTemplate(
            input_variables=["job_description"],
            template="Try to Summarize the Job Desription mentioning all the skillset in about 100 to 150 words: {job_description}."
        )

        parser = StrOutputParser()

        chain = prompt_summarizer | self.model | parser
        self.jd_documents = chain.invoke({"job_description":document})
        
        
    def context_generator(self,title,question):
        class Context(BaseModel):
            context: Literal["Experience", "Coding", "Knowledge"] = Field(description="Sentiment of the feedback")
        
        parser_context = PydanticOutputParser(pydantic_object=Context)
        
        prompt_context = PromptTemplate(
            input_variables=["job_position","job_description","question"],
             partial_variables={"format_instructions": parser_context.get_format_instructions()},
            template='''You are the technical Expert with 11+Years of experience for the project title {job_position}.
            And You have all the Experince mentioned in the {job_description}.
            You are facing the interview for the same job position {job_position}
            
            Now Based on the question {question} asked by the interviewer try to extract the context of the question that has been asked by the interviewer.
            
            The context may be 'Experience' when asked about your epericence in the related technology and project.
            The context may be 'Coding' when asked about coding epericence in the related technology.
            The context may be 'Knowledge' when asked about knowledge in the related technology and project.
            
            Do not try to explain why you choose one of the context just give one of the context in any question asked.
            
            \n {format_instructions}
            '''
        )

        
        chain = prompt_context | self.model | parser_context
        question = chain.invoke({"job_position":title,
                                 "job_description": self.jd_documents,
                                 "question": question})
        return question.context
                
        
