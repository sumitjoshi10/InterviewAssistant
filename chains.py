from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate,ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser,PydanticOutputParser
from langchain_core.runnables import RunnablePassthrough,RunnableParallel,RunnableBranch,RunnableLambda

from pydantic import BaseModel,Field
from doc_loader import DocumnetLoader
from vector_store import VectorStore

from typing import Literal, Dict

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
        
         # Parsers
        self.parser_str = StrOutputParser()
        self.parser_context = self._create_context_parser()

        # Chains
        self.jd_summarizer_chain = self._create_jd_summarizer_chain()
        self.context_chain = self._create_context_chain()
        self.code_chain = self._create_code_chain()
        self.knowledge_chain = self._create_knowledge_chain()
        self.experience_prompt = self._create_experience_prompt()

    def _create_context_parser(self) -> PydanticOutputParser:
        class Context(BaseModel):
            context: Literal["Experience", "Coding", "Knowledge"] = Field(description="Context of the Question")
        return PydanticOutputParser(pydantic_object=Context)
    
    def _create_jd_summarizer_chain(self):
        prompt = PromptTemplate(
            input_variables=["job_description"],
            template="Try to Summarize the Job Description mentioning all the skillset in about 100 to 150 words: {job_description}."
        )
        return prompt | self.model | self.parser_str

    def _create_context_chain(self):
        
        prompt = PromptTemplate(
            input_variables=["job_position", "job_description", "question"],
            template='''
                You are the technical Expert with 11+Years of experience for the project title {job_position}.
                And you have all the experience mentioned in the {job_description}.
                You are facing the interview for the same job position {job_position}.
                Based on the question {question} asked by the interviewer, try to extract the context of the question.

                Contexts:
                - 'Experience': when asked about your experience in the related technology.
                - 'Coding': when asked about code-level questions.
                - 'Knowledge': when asked about conceptual or theoretical questions.

                Just return the context. No explanation.
                {format_instructions}
            ''',
            partial_variables={"format_instructions": self.parser_context.get_format_instructions()}
        )
        return prompt | self.model | self.parser_context

    def _create_code_chain(self):
        prompt = ChatPromptTemplate([
            ("system", '''
                You are a helpful coding assistant for the role {job_position} with expertise in:
                {job_description}
                Based on the following question, generate only the code in the required language.
                Think step-by-step.
            '''),
            ("user", "Write the code for the question: {question}")
        ])
        return prompt | self.model | self.parser_str
    
    def _create_knowledge_chain(self):
        prompt = ChatPromptTemplate([
            ("system", '''
                You are a technical expert for {job_position}, skilled in:
                {job_description}
                Provide a direct, concise, bullet-point answer to the following question.
                Avoid over-explaining or fluff. Start each point on a new line.
                If you don't know, say so.
            '''),
            ("user", "Answer this question: {question}")
        ])
        return prompt | self.model | self.parser_str
    
    def _create_experience_prompt(self):
        return ChatPromptTemplate([
            ("system", '''
                You are a helpful technical expert assistant for the job position: {job_position}.
                Based on the job description:
                {job_description}
                And the resume context:
                {resume_context}
                Answer the interview question from the perspective of your past experiences,
                using all projects/companies. Use concise bullet points.
            '''),
            ("user", "Share your experience matching the context for the question: {question}")
        ])
    
    def jd_summarizer_invoke(self, jd_file):
        try:
            jd_document = self.doc_loader.jd_loader(jd_file=jd_file)
            return self.jd_summarizer_chain.invoke({"job_description": jd_document})
        except Exception as e:
            st.error(f"JD Summarization Error: {e}")
            
    def generate_vector_store(self, resume_file):
        try:
            resume_document = self.doc_loader.resume_loader(resume_file=resume_file)
            self.vector_store = self.vector_store_object.vector_store(document=resume_document)
            st.success("Vector Store ID: " + str(self.vector_store.index_to_docstore_id))
        except Exception as e:
            st.error(f"Vector Store Generation Error: {e}")
            
    
    
    def context_generator_chain(self):

        return self.context_chain

    def merge_context(self, parsed_output: BaseModel, original_input: Dict[str, str]) -> Dict[str, str]:
        return {
            "context": parsed_output.context,
            "job_position": original_input.get("job_position", ""),
            "job_description": original_input.get("job_description", ""),
            "question": original_input.get("question", "")
        }

    def code_generator_chain(self):
        return self.code_chain

    def knowledge_generator_chain(self):
        return self.knowledge_chain

    def format_docs(self, retrieved_docs):
        return "\n\n".join(doc.page_content for doc in retrieved_docs)
    

    def experience_generation_chain(self):
        try:
            if self.vector_store is None:
                raise ValueError("Vector store not initialized.")
            
            self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 5},search_type="similarity")
            experience_parallel_chain = RunnableParallel({
                "resume_context": RunnableLambda(lambda x: self.retriever.invoke(x["question"])) | RunnableLambda(self.format_docs),
                "job_position": RunnableLambda(lambda x: x["job_position"]),
                "job_description": RunnableLambda(lambda x: x["job_description"]),
                "question": RunnableLambda(lambda x: x["question"]),
            })
            # return experience_parallel_chain
            return experience_parallel_chain | self.experience_prompt | self.model | self.parser_str
        except Exception as e:
            st.error(f"Experience Chain Error: {e}")