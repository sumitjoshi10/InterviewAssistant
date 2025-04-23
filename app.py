import streamlit as st
from streamlit_mic_recorder import speech_to_text
from models import AnswerGenerator


import os
import certifi

os.environ["SSL_CERT_FILE"] = certifi.where()

state = st.session_state

# Initialize state
if "question" not in state:
    state.question = ""
if "answer" not in state:
    state.answer = {}
if "manual_input" not in state:
    state.manual_input = ""
if "model" not in state:
    state.model = AnswerGenerator()
if "context" not in state:
    state.context = ""
if "jd_summarized_document" not in state:
    state.jd_summarized_document = ""
if "resume_vector_store" not in state:
    state.resume_vector_store = ""
    
# Callback function when Enter is pressed
def handle_submit():
    state.STT_output = ""
    state.STT = None
    state.question = state.manual_input
    state.manual_input = ""  # Clear the input field

# state

# Sidebar button logic
with st.sidebar:
    st.markdown("## Control Panel")
    text = speech_to_text(start_prompt="🟢 Start Recoding",
                          stop_prompt="🔴 Stop Recoding",
                          language='en', 
                          use_container_width=True, 
                          just_once=False, key='STT'
                        )
    
 # If audio text is detected and no manual input, handle it
    if text and not state.get("manual_input"):
        state.question = text

  

    # Manual text input field using a different key
    st.text_input(
        "Enter the question:",
        key="manual_input",
        on_change=handle_submit
    )

    ## Context Markdown
    st.markdown(
        f"**Context:** {state.context}"
    )
    
    
    # Simulated second sidebar using expander
    with st.expander("📂 Document Uploader", expanded=False):
        st.markdown("Need to Upload the Resume and JD here")
        
        ## Get the Job Position Here
        job_position = st.text_input("Job Position")
        
        ## Upload the Resume
        resume_file = st.file_uploader("Upload your Resume (.docx only)", type=["docx"])
        if resume_file and state.resume_vector_store == "":
            
            state.resume_vector_store = state.model.resume_vector_store(resume_file)
        elif not resume_file:
            state.resume_vector_store = ""
            
        ## Upload the Job Description
        jd_file = st.file_uploader("Upload your Job Description (.txt only)", type=["txt"])
        if jd_file and state.jd_summarized_document == "":
            state.jd_summarized_document = state.model.jd_summarizer(jd_file=jd_file)
        elif not jd_file:
            state.jd_summarized_document = ""
            
            

    st.markdown("-----")
    st.markdown("Made by Sumit Joshi")
    
    

# Main page content
st.title(f"Interview Assistant for Job position {job_position}")

st.markdown(
        f"**Resume:** {'✅  Uploaded and Vectorized' if state.resume_vector_store else '❌ Pending'}"
    )
st.markdown(
        f"**Job Description:** {'✅  Uploaded and Summarized' if state.jd_summarized_document else '❌ Pending'}"
    )

if jd_file and resume_file and state.question and job_position:
    state.answer = state.model.answer_generator(job_position=job_position,question=state.question)
    state.context = state.answer["context"].context



### To dispaly Context
st.markdown(
    f"<p style='font-size:30px; color:White;'> <b>Context: </b>{state.context}",
    unsafe_allow_html=True
)

### To Display Question
st.markdown(
    f"<p style='font-size:30px; color:White;'> <b>Question: </b><br> {state.question}</p>",
    unsafe_allow_html=True
)

### Change the Resume to Vector
if state.resume_vector_store:
    st.write(state.resume_vector_store)
    
# Just to check the Job Description
if state.jd_summarized_document:    
    st.write(state.jd_summarized_document)




# Conditional markdown for answer
if state.question:
    answer = state.answer["answer"]
    msg = f"<p style='font-size:30px; color:White;'><b>Answer: </b><br> {answer} </p>"
else:
    msg = ""
st.markdown(msg, unsafe_allow_html=True)
