import streamlit as st
import os
from groq import Groq
import pytesseract
from PIL import Image
import io
import requests
import time
import fitz  # PyMuPDF

# Initialize session state for each input type
if 'text_responses' not in st.session_state:
    st.session_state.text_responses = []
if 'image_responses' not in st.session_state:
    st.session_state.image_responses = []
if 'pdf_responses' not in st.session_state:
    st.session_state.pdf_responses = []

# Initialize Groq client
GROQ_API_KEY = "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"

client = Groq(api_key=GROQ_API_KEY)

# Initialize OCR
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update this path for Windows

def process_image(image_file):
    try:
        image = Image.open(image_file)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return None

def extract_text_from_pdf(pdf_file):
    try:
        text = ""
        pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)
            text += page.get_text()
        return text
    except Exception as e:
        st.error(f"Error processing PDF: {str(e)}")
        return None

def get_ai_response(input_text, topic_type):
    try:
        system_message = """you are an AI study assistant. Provide hints and approaches to solve problems, but don't give exact answers. 
        When crafting your response, consider the following prompts and guidelines:the answershould be versatile and arises curiosity in the user and do not reveal the exact answers give them hints to solve a particular solution . you should tell them that you could not give them exact anwer if they demand .
        Ensure each hint is unique and encourages critical thinking. Focus on {topic_type}-related """
        if topic_type == "Coding":
            system_message += "Focus on coding-related topics and provide specific coding hints."
        elif topic_type == "Math":
            system_message += "Focus on math-related topics and provide specific mathematical hints."
        elif topic_type == "Science":
            system_message += "Focus on science-related topics and provide specific scientific hints."
        else:
            system_message += "Focus on general education-related topics."

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_message
                },
                {
                    "role": "user",
                    "content": input_text,
                }
                {
                "role": "user",
                "content": "Can you recommend resources (books, YouTube videos, articles, related quizzes, and interview questions) related to the topic mentioned above?"
                }
            ],
            model="llama-3.1-70b-versatile",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        st.error(f"Error getting AI response: {str(e)}")
        return None

# Streamlit UI
st.set_page_config(page_title="AI Study Assistant", page_icon="📚", layout="wide")
st.markdown("""
<style>
    /* Overall app background */
    .stApp {
        background: linear-gradient(to bottom right, #f3f4f6, #e0e7ff);
    }
    
    /* Center main content */
    .stContainer {
        max-width: 800px;
        padding: 20px;
        margin: 0 auto;
    }

    /* Header styling */
    .main-header {
        background: linear-gradient(45deg, #4F46E5, #6366F1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5em;
        text-align: center;
        font-weight: bold;
    }

    /* Subheader styling */
    .sub-header {
        background: linear-gradient(45deg, #F87171, #EF4444);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 1.2em;
        text-align: center;
        margin-top: -10px;
    }

    /* Text input styling */
    .stTextArea textarea {
        background-color: #ffffff;
        border: 1px solid #d1d5db;
        border-radius: 10px;
        padding: 15px;
        font-size: 1em;
        color: #374151;
    }

    /* File uploader styling */
    .stFileUploader {
        background-color: #ffffff;
        border: 1px dashed #9CA3AF;
        border-radius: 10px;
        padding: 15px;
        color: #374151;
        margin: 15px 0;
    }

    /* Response card styling */
    .response-card {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.05);
    }

    /* Hint text styling */
    .hint-text {
        background-color: #f9fafb;
        border-left: 5px solid #3B82F6;
        border-radius: 5px;
        padding: 15px;
        font-size: 0.9em;
        color: #374151;
        margin-top: 10px;
    }

    /* Button styling */
    .stButton > button {
        background-color: #6366F1;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: bold;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #e0e7ff;
        color: #4B5563;
        border-radius: 5px 5px 0 0;
    }

    .stTabs [aria-selected="true"] {
        background-color: #6366F1;
        color: white;
    }

    /* Footer styling */
    .footer {
        background: linear-gradient(45deg, #CBD5E1, #9CA3AF);
        color: #374151;
        text-align: center;
        padding: 10px;
        font-size: 0.9em;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)


# Sidebar
st.sidebar.image("Q.png", width=250)
topic_type = st.sidebar.radio("Topic type:", ("General", "Machine Learning & Data Mining", "Neuron Networks and Deep Learning", "Computer Networks"))

# Main content
st.markdown("<h1 class='main-header'>AI Study Assistant</h1>", unsafe_allow_html=True)
st.markdown("<h2 class='sub-header'>Welcome! How can we help you today?</h2>", unsafe_allow_html=True)

# Create tabs for different input types
text_tab, image_tab, pdf_tab = st.tabs(["Text Input", "Image Input", "PDF Input"])

with text_tab:
    user_input = st.text_area("Enter your question:")
    if st.button("Get Hint (Text)"):
        with st.spinner("Processing..."):
            if user_input:
                hint = get_ai_response(user_input, topic_type)
                if hint:
                    st.markdown("<div class='response-card'>", unsafe_allow_html=True)
                    st.markdown("### Hint:")
                    st.markdown(f'<div class="hint-text">{hint}</div>', unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    st.session_state.text_responses.append((user_input, hint))
            else:
                st.warning("Please enter a question.")
    
    # Display text chat history
    if st.session_state.text_responses:
        st.markdown("### Previous Text Responses:")
        for i, (question, answer) in enumerate(reversed(st.session_state.text_responses), 1):
            st.markdown("<div class='response-card'>", unsafe_allow_html=True)
            st.markdown(f"<h4>Question {i}:</h4>", unsafe_allow_html=True)
            st.write(question)
            st.markdown(f"<h4>Answer {i}:</h4>", unsafe_allow_html=True)
            st.markdown(f'<div class="hint-text">{answer}</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            if i < len(st.session_state.text_responses):
                st.markdown("<div class='response-divider'></div>", unsafe_allow_html=True)

with image_tab:
    image_file = st.file_uploader("Upload image file", type=["png", "jpg", "jpeg"])
    if st.button("Get Hint (Image)"):
        with st.spinner("Processing..."):
            if image_file:
                text = process_image(image_file)
                if text:
                    hint = get_ai_response(text, topic_type)
                    if hint:
                        st.markdown("<div class='response-card'>", unsafe_allow_html=True)
                        st.markdown("### Processed text:")
                        st.write(text)
                        st.markdown("### Hint:")
                        st.markdown(f'<div class="hint-text">{hint}</div>', unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                        st.session_state.image_responses.append((text, hint))
            else:
                st.warning("Please upload an image.")
    
    # Display image chat history
    if st.session_state.image_responses:
        st.markdown("### Previous Image Responses:")
        for i, (question, answer) in enumerate(reversed(st.session_state.image_responses), 1):
            st.markdown("<div class='response-card'>", unsafe_allow_html=True)
            st.markdown(f"<h4>Processed Text {i}:</h4>", unsafe_allow_html=True)
            st.write(question)
            st.markdown(f"<h4>Answer {i}:</h4>", unsafe_allow_html=True)
            st.markdown(f'<div class="hint-text">{answer}</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            if i < len(st.session_state.image_responses):
                st.markdown("<div class='response-divider'></div>", unsafe_allow_html=True)

with pdf_tab:
    pdf_file = st.file_uploader("Upload PDF file", type=["pdf"])
    if st.button("Get Hint (PDF)"):
        with st.spinner("Processing..."):
            if pdf_file:
                text = extract_text_from_pdf(pdf_file)
                if text:
                    hint = get_ai_response(text, topic_type)
                    if hint:
                        st.markdown("<div class='response-card'>", unsafe_allow_html=True)
                        st.markdown("### Processed text:")
                        st.write(text[:500] + "..." if len(text) > 500 else text)  # Show first 500 characters
                        st.markdown("### Hint:")
                        st.markdown(f'<div class="hint-text">{hint}</div>', unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                        st.session_state.pdf_responses.append((text, hint))
            else:
                st.warning("Please upload a PDF file.")
    
    # Display PDF chat history
    if st.session_state.pdf_responses:
        st.markdown("### Previous PDF Responses:")
        for i, (question, answer) in enumerate(reversed(st.session_state.pdf_responses), 1):
            st.markdown("<div class='response-card'>", unsafe_allow_html=True)
            st.markdown(f"<h4>Processed Text {i}:</h4>", unsafe_allow_html=True)
            st.write(question[:500] + "..." if len(question) > 500 else question)  # Show first 500 characters
            st.markdown(f"<h4>Answer {i}:</h4>", unsafe_allow_html=True)
            st.markdown(f'<div class="hint-text">{answer}</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            if i < len(st.session_state.pdf_responses):
                st.markdown("<div class='response-divider'></div>", unsafe_allow_html=True)

# Footer
st.markdown("<div class='footer'>© 2024 AI Study Assistant. All rights reserved.</div>", unsafe_allow_html=True)

# Progress bar in sidebar
progress_bar = st.sidebar.progress(0)
for i in range(100):
    time.sleep(0.01)
    progress_bar.progress(i + 1)
st.sidebar.success("Ready!")
