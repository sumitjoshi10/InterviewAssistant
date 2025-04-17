import streamlit as st

# Callback function to toggle the state
def toggle():
    st.session_state.running = not st.session_state.running
    if st.session_state.running:
        st.session_state.question = ""
    else:
        st.session_state.question = "From Mic"
    
# Callback function when Enter is pressed
def handle_submit():
    st.session_state.question = st.session_state.user_input
    st.session_state.user_input = ""  # Clear input

# Initialize the state
if "running" not in st.session_state:
    st.session_state.running = False
if "question" not in st.session_state:
    st.session_state.question = ""

# Sidebar button logic
with st.sidebar:
    st.markdown("## Control Panel")
    st.button(
        "▶️ Start" if not st.session_state.running else "⏹️ Stop",
        key="toggle_button",
        on_click=toggle,
    )
    st.markdown(
        f"**Status:** {'🟢 Running' if st.session_state.running else '🔴 Stopped'}"
    )
    ## to take the user Input 
    new_input = st.text_input(
        "Enter the question:", 
        key="user_input",
        on_change=handle_submit,
        disabled=st.session_state.running
    )
    
    
    # Simulated second sidebar using expander
    with st.expander("📂 Document Uploader", expanded=False):
        st.markdown("Need to Upload the Resume and JD here")
        
        ## Get the Job Position Here
        job_position = st.text_input("Job Position")
        
        ## Upload the Resume
        resume_file = st.file_uploader("Upload your Resume (.docx only)", type=["docx"])
        
        ## Upload the Job Description
        jd_file = st.file_uploader("Upload your Job Description (.txt only)", type=["txt"])

    st.markdown("-----")
    st.markdown("Made by Sumit Joshi")
    
    


# Main page content
st.title(f"Interview Assistant for Job position {job_position}")

st.markdown(
        f"**Resume:** {'✅  Uploaded' if resume_file else '❌ Pending'}"
    )
st.markdown(
        f"**Job Description:** {'✅  Uploaded' if jd_file else '❌ Pending'}"
    )
st.markdown(
    f"<p style='font-size:30px; color:White;'> <b>Question: </b><br> {st.session_state.question}</p>",
    unsafe_allow_html=True
)

