from chains import Chains
from doc_loader import DocumnetLoader
from langchain_core.prompts import PromptTemplate,ChatMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser,PydanticOutputParser
from langchain_core.runnables import RunnablePassthrough,RunnableParallel,RunnableBranch,RunnableLambda
from langchain_community.document_loaders import TextLoader,Docx2txtLoader


import streamlit as st
from pydantic import BaseModel, Field
from typing import Literal

doc_loader = DocumnetLoader()

class AnswerGenerator:
    def __init__(self):
        self.chains = Chains()
        self.jd_documents = []
        self.resume_documents = []
                     
    def jd_summarizer(self, jd_file):
        '''Will summarize the Document using the chains'''
        try:
            jd_document =doc_loader.jd_loader(jd_file=jd_file)
            jd_summarizer_chain = self.chains.jd_summarizer_chain()
            self.jd_documents = jd_summarizer_chain.invoke({"job_description":jd_document})
            # print (self.jd_documents)
            return self.jd_documents ### only to test
        
        except Exception as e:
            st.error(e)
    
    def resume_vector_store(self, resume_file):
        '''Will convert the Document to the Vector Store'''
        try:
            resume_document = doc_loader.resume_loader(resume_file=resume_file)
            
            ## Need to code to store in the Vector Store
            ## For now just returing the Document that has been Uploaded
            return resume_document
        except Exception as e:
            st.error(e)
            
                 
    def answer_generator(self, job_position="", question=""):
        context_chain = self.chains.context_generator_chain()
        
        knowledge_answer_chain = RunnableLambda(lambda x: "Knowledge Chain Activated")
        code_answer_chain = RunnableLambda(lambda x: "Coding Chain Activated")
        experience_answer_chain = RunnableLambda(lambda x: "Expericence Chain Activated")
        default_answer_chain = RunnableLambda(lambda x: "Default Chain Activated")
        
        branch_chain = RunnableBranch(
            (lambda x:x.context == "Experience", experience_answer_chain),
            (lambda x:x.context == "Coding", code_answer_chain),
            (lambda x:x.context == "Knowledge", knowledge_answer_chain),
            default_answer_chain
        )
        # branch_chain = RunnableLambda(lambda x: "Branch Chain Activated")
        
        parallel_chain = RunnableParallel({
            "context": RunnablePassthrough(),
            "answer" : branch_chain
        })
     
        chain = context_chain | parallel_chain
       
        
              
        answer = chain.invoke({"job_position":job_position,
                                 "job_description": self.jd_documents,
                                 "question": question})
        
        # answer = chain.invoke({"job_position":"GEn AI",
        #                      "job_description": "We're seeking a Mid-Level Generative AI Developer with expertise in Python, AI-focused libraries (PyTorch, TensorFlow, LangChain, Transformers), and AWS services. The ideal candidate will have hands-on experience with AWS Bedrock, Knowledge Base, and LLM models, as well as knowledge of Retrieval-Augmented Generation (RAG) models, vector databases, and AWS Serverless Technologies. Key skills include Python, AI/ML-focused libraries, AWS services (Lambda, API Gateway, Step Functions, S3, DynamoDB), MLOps practices, and CI/CD pipelines. The candidate should also have experience with RAG models, vector databases, and cloud-based AI deployment, with strong problem-solving skills and analytical thinking. Additionally, knowledge of prompt engineering, multi-modal AI models, and AWS AI services is preferred.",
        #                      "question": "Write the code on FAST API"})
        
        return answer
        
        
if __name__ =="__main__":
    
    import os
    import certifi
    os.environ["SSL_CERT_FILE"] = certifi.where()

    answer = AnswerGenerator().answer_generator()
    print(answer)
    print(answer["context"])
    print(type(answer["context"]))
    print(answer["context"].context)

        
