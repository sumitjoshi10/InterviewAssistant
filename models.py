from chains import Chains
from doc_loader import DocumnetLoader
from vector_store import VectorStore

from langchain_core.runnables import RunnablePassthrough,RunnableParallel,RunnableBranch,RunnableLambda
from logger import logging


import streamlit as st

class AnswerGenerator:
    def __init__(self):
        self.chains = Chains()
        self.jd_documents = []
        
        
         # Pre-initialize chains (optimization)
        
        self.context_chain = self.chains.context_generator_chain()
        self.knowledge_chain = self.chains.knowledge_generator_chain()
        self.code_chain = self.chains.code_generator_chain()
        
                     
    def jd_summarizer(self, jd_file):
        '''Will summarize the Document using the chains'''
        try:
            logging.info("JD Summarization started")
            self.jd_documents = self.chains.jd_summarizer_invoke(jd_file=jd_file)
            logging.info("JD Summarization completed")
            
            # print (self.jd_documents)
            return True ### only to test
        
        except Exception as e:
            logging.info("JD Summarization Error: ", e)
            st.error("Jd Summarization Error: ", e)
            return False
    
    def resume_vector_store(self, resume_file):
        '''Will convert the Document to the Vector Store'''
        try:
            logging.info("Vector Store Generation started")
            self.chains.generate_vector_store(resume_file=resume_file)
            logging.info("Vector Store Generation Completed")
            logging.info("Experience Chain Generation started")
            self.experience_chain = self.chains.experience_generation_chain()
            logging.info("Experience Chain Generation Completed")
            return True
           
        except Exception as e:
            logging.info("Vector Store Generation Error: ", e)
            st.error("Vector Store Generation Error: ", e)
            return False
            
                 
    def answer_generator(self, job_position="", question=""):
        try:
            
            ### STEP 1: Combine context_chain output with original input
            ### Merging the Input as well as output from the Context Chain
            logging.info("Merging Context Chain started")
            merge_context_chain = RunnableLambda(lambda inputs: self.chains.merge_context(inputs["parsed"], inputs["original"]))
            logging.info(f"Merging Context Chain Completed: \n {merge_context_chain}")
          
            
            
            # First, run the context_chain and capture both the parsed output and original input
            logging.info("Combined Chain started")
            combined_chain = RunnableLambda(lambda x: {"parsed": self.context_chain.invoke(x), "original": x}) | merge_context_chain
            logging.info(f"Combined Chain completed \n {combined_chain}")
            
            
            
            # STEP 2: Route based on context
            logging.info("Branch Chain started")
            branch_chain = RunnableBranch(
                
                (lambda x: x["context"] == "Coding", self.code_chain),
                (lambda x: x["context"] == "Knowledge", self.knowledge_chain),
                (lambda x: x["context"] == "Experience", self.experience_chain),
                self.knowledge_chain  # default
            )
            logging.info(f"Branch Chain Completed\n {branch_chain}")
            
            
             # STEP 3: Parallel Chain
            logging.info("Parallel Chain started")
            parallel_chain = RunnableParallel({
                "context": RunnableLambda(lambda x: x["context"]),
                "answer": branch_chain
            })
            logging.info(f"Parallel Chain Completed \n {parallel_chain}")
            
            # STEP 4 : Full chain
            logging.info("Final Chain started")
            final_chain = combined_chain | parallel_chain
            logging.info(f"Final Chain Completed \n {final_chain}")
            
        
        
            ## Invoke the chain with proper input structure
            answer = final_chain.invoke({
                "job_position": job_position,
                "job_description": self.jd_documents,
                "question": question
            })
            
            # answer = final_chain.invoke({
            #     "job_position": "GEN AI",
            #     "job_description": "We are seeking a Mid-Level Generative AI Developer with expertise in Python, AI-focused libraries (PyTorch, TensorFlow, LangChain, Transformers), and AWS services. The ideal candidate should have hands-on experience with AWS Bedrock, AWS Knowledge Base, and LLM models. Key skills include Python, AI/ML development, AWS Serverless Technologies (Lambda, API Gateway, Step Functions), RAG models, vector databases, and MLOps practices. Additionally, experience with AWS AI services, prompt engineering, and multi-modal AI models is preferred. The candidate should have strong problem-solving skills, analytical thinking, and the ability to work independently or in a team environment, with a focus on designing, developing, and deploying cutting-edge AI solutions using AWS services and Python.",
            #     # "question": "What is your experience with AWS Bedrock?"
            #     "question": "Write the code to add 2 number"
            # })
            
            
            return answer
        
        except Exception as e:
            st.error(e)
        
if __name__ =="__main__":
    
    import os
    import certifi
    os.environ["SSL_CERT_FILE"] = certifi.where()

    answer = AnswerGenerator().answer_generator()
    if answer is not None and "context" in answer:
        print(answer)
        print(answer["context"])
        print(type(answer["context"]))
        print(answer["answer"])

    else:
        print("No context found or answer is None.")
    

