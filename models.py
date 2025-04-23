from chains import Chains
from doc_loader import DocumnetLoader

from langchain_core.runnables import RunnablePassthrough,RunnableParallel,RunnableBranch,RunnableLambda


import streamlit as st


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
        code_answer_chain = self.chains.code_generator_chain()
        experience_answer_chain = RunnableLambda(lambda x: "Experience Chain Activated")
        default_answer_chain = RunnableLambda(lambda x: "Default Chain Activated")
        
        branch_chain = RunnableBranch(
            (lambda x: x["context"] == "Experience", experience_answer_chain),
            (lambda x: x["context"] == "Coding", code_answer_chain),
            (lambda x: x["context"] == "Knowledge", knowledge_answer_chain),
            default_answer_chain
        )
        
        
        ### Merging the Input as well as output from the Context Chain
        merge_context_chain = RunnableLambda(lambda inputs: self.chains.merge_context(inputs["parsed"], inputs["original"]))
        
        
        # First, run the context_chain and capture both the parsed output and original input
        combined_chain = RunnableLambda(lambda x: {"parsed": context_chain.invoke(x), "original": x}) | merge_context_chain
      
            
        parallel_chain = RunnableParallel({
            "context": RunnableLambda(lambda x: x["context"]),
            "answer": branch_chain
        })
     
        # Full chain
        final_chain = combined_chain | parallel_chain
       
        #### Invoke the chain with proper input structure
        answer = final_chain.invoke({
            "job_position": job_position,
            "job_description": self.jd_documents,
            "question": question
        })
        
        # answer = final_chain.invoke({
        #     "job_position": "GEN AI",
        #     "job_description": "We are seeking a Mid-Level Generative AI Developer with expertise in Python, AI-focused libraries (PyTorch, TensorFlow, LangChain, Transformers), and AWS services. The ideal candidate should have hands-on experience with AWS Bedrock, AWS Knowledge Base, and LLM models. Key skills include Python, AI/ML development, AWS Serverless Technologies (Lambda, API Gateway, Step Functions), RAG models, vector databases, and MLOps practices. Additionally, experience with AWS AI services, prompt engineering, and multi-modal AI models is preferred. The candidate should have strong problem-solving skills, analytical thinking, and the ability to work independently or in a team environment, with a focus on designing, developing, and deploying cutting-edge AI solutions using AWS services and Python.",
        #     "question": "Write the code to sum 2 number"
        # })
        
        
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


