from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate,ChatMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser,PydanticOutputParser
from pydantic import BaseModel,Field

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
          
    def jd_summarizer_chain(self):
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
    
    def context_generator_chain(self):
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
        
        context_chain = prompt_context | self.model | parser_context
        return context_chain
