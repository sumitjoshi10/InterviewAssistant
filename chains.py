from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate,ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser,PydanticOutputParser
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from pydantic import BaseModel,Field
from doc_loader import DocumnetLoader
from vector_store import VectorStore

from typing import Literal

import streamlit as st

from dotenv import load_dotenv
import os

load_dotenv()

class Chains:
    def __init__(self):
        self.model = ChatGroq(
            model_name="llama-3.3-70b-versatile",
            temperature=0.7,
            api_key=os.getenv("GROQ_API_KEY")
        )
        self.doc_loader = DocumnetLoader()
        self.vector_store_object = VectorStore()
        self.vector_store = None
          
    def _jd_summarizer_chain(self):
        '''It is the Chain used to summarize the JD'''
        try:
            prompt_summarizer = PromptTemplate(
                input_variables=["job_description"],
                template="Try to Summarize the Job Desription mentioning all the skillset in about 100 to 150 words: {job_description}."
            )

            parser = StrOutputParser()

            jd_chain = prompt_summarizer | self.model | parser
            return jd_chain
        except Exception as e:
            st.error(e)
            
    def jd_summarizer_invoke(self,jd_file):
        '''This function will invoke the JD summarizer chain and return the summarized JD
            It will take the JD file and convert it to the text and then summarize it'''
            
        try:
            jd_document =self.doc_loader.jd_loader(jd_file=jd_file)
            jd_summarizer_chain = self._jd_summarizer_chain()
            jd_summarized = jd_summarizer_chain.invoke({"job_description":jd_document})
            return jd_summarized
        except Exception as e:
            st.error(e)
            
    def generate_vector_store(self,resume_file):
        '''This function will generate the vector store for the resume file
            It will take the resume file and convert it to the vector store'''
            
        try:
            resume_document = self.doc_loader.resume_loader(resume_file=resume_file)
            self.vector_store = self.vector_store_object.vector_store(document=resume_document)
            
            st.success("Vector Store ID: "+str(self.vector_store.index_to_docstore_id))
            print (self.vector_store.index_to_docstore_id)
        except Exception as e:
            st.error(e)
        
    def context_generator_chain(self):
        '''This function will generate the context for the question asked by the interviewer
            It will take the job position, job description and question asked by the interviewer
            It will return the context of the question asked by the interviewer'''
            
        try:
            class Context(BaseModel):
                context: Literal["Experience", "Coding", "Knowledge"] = Field(description="Context of the Question")
            
            parser_context = PydanticOutputParser(pydantic_object=Context)
            
            prompt_context = PromptTemplate(
                input_variables=["job_position","job_description","question"],
                
                template='''You are the technical Expert with 11+Years of experience for the project title {job_position}.
                And you have all the experience mentioned in the {job_description}.
                You are facing the interview for the same job position {job_position}.
                
                Now based on the question {question} asked by the interviewer, try to extract the context of the question.
                
                The context may be:
                - 'Experience': when asked about your experience in the related technology and project.
                - 'Coding': when asked about coding experience in the related technology.
                - 'Knowledge': when asked about knowledge in the related technology and project.
                
                Do not try to explain why you chose the context. Just give one of the context values.
                
                {format_instructions}
                ''',
                partial_variables={"format_instructions": parser_context.get_format_instructions()},
            )
            
            context_chain = prompt_context | self.model | parser_context
            return context_chain
        except Exception as e:
            st.error(e)
    
       
    def merge_context(self,parsed_output, original_input):
        '''This function will merge the context with the original input
            It will take the parsed output and original input and return the merged output
            It will take the context from the parsed output and job position, job description and question from the original input
            It will return the merged output as a dictionary'''
        try:
            return {
                "context": parsed_output.context,
                "job_position": original_input.get("job_position", ""),
                "job_description": original_input.get("job_description", ""),
                "question": original_input.get("question", "")
            }
        except Exception as e:
            st.error(e)
        
    def code_generator_chain(self):
        '''This function will generate the code for the question asked by the interviewer
            It will take the job position, job description and question asked by the interviewer
            It will return the code chain for the question asked by the interviewer'''
            
        try:
            parser_code = StrOutputParser()
            
            system_template = ('''
            You are a helpful coding assistant with expert in Job position {job_position} having all the knowledge of all the mentioned skills in job description as 
            
            {job_description}
            
            Now Based on the question asked by the interviewer.
            Your job is to output only code in the specified programming language.

            Think step by step and provide a concise answer
            ''')
            prompt_code = ChatPromptTemplate([
                ("system",system_template),
                ("user","Write the code for the question \n {question}"),
                ])
            
            code_chain = prompt_code | self.model | parser_code
            return code_chain
        
        except Exception as e:
            st.error(e)

    def knowledge_generator_chain(self):
        try:
           
            parser_knowledge = StrOutputParser()
            
            system_template = ('''
            You are a helpful technical Expert assistant with expert in Job position {job_position} having all the knowledge of all the mentioned skills in job description as 
            
            {job_description}
            
            Now Based on the question asked by the interviewer.
            Your job is to provide the relevant answer only along with the Matematical Equation if Required without code snippet.
            
            Using all your Experties knowledge give to the point short and consice answer.
            Do not try to explain everthing.
            
            Try to give answer only in bullet points.
            Each Bullet Point shold begin in New Line
            
            If the Question is not in the context of your experties please say you dnt know.
        
            ''')
            prompt_knowledge = ChatPromptTemplate([
                ("system",system_template),
                ("user","Write the code for the question \n {question}"),
                ])
            
            knowledge_chain = prompt_knowledge | self.model | parser_knowledge
            return knowledge_chain
        except Exception as e:
            st.error(e)