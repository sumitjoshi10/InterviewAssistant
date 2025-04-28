import tempfile
import os
import streamlit as st

from langchain_community.document_loaders import TextLoader,Docx2txtLoader


class DocumnetLoader:
    def __init__(self):
        self.temp_path = None

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
            return document[0].page_content  ### to check whether it is generating the response
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
            return document
            # return document[0].page_content ### to check whether it is generating the response
        except Exception as e:
            st.error(e)
        finally:
            self._clean_up()