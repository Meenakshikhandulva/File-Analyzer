import streamlit as st
import pandas as pd
import PyPDF2
import re
import base64

# Function to analyze CSV files
def analyze_csv(file):
    df = pd.read_csv(file)
    return {
        "Shape": df.shape,
        "Columns": df.columns.tolist(),
        "Description": df.describe(),
        "Head": df.head().to_dict(orient='records'),
        "Content": df.to_string()  # Convert DataFrame to string for context
    }

# Function to analyze TXT files
def analyze_txt(file):
    content = file.read().decode("utf-8")
    lines = content.splitlines()
    return {
        "Line Count": len(lines),
        "First 5 Lines": lines[:5],
        "Content": content  # Store content for question answering
    }

# Function to analyze PDF files
def analyze_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ''
    for page in reader.pages:
        text += page.extract_text() + '\n'
    lines = text.splitlines()
    return {
        "Page Count": len(reader.pages),
        "Line Count": len(lines),
        "First 5 Lines": lines[:5],
        "Content": text  # Store content for question answering
    }

# Question-answering function
def answer_question(question, context):
    sentences = re.split(r'[.!?]+', context)
    best_score = 0
    best_sentence = ''
    for sentence in sentences:
        score = sum(1 for word in question.lower().split() if word in sentence.lower().split())
        if score > best_score:
            best_score = score
            best_sentence = sentence.strip()
    
    return best_sentence if best_sentence else "No relevant answer found."

# Function to load and encode the background image
def load_background_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return f"data:image/jpeg;base64,{encoded_string}"

# Streamlit UI
st.set_page_config(page_title="File Analysis App", layout="wide")

# Load the background image
bg_image = load_background_image(r"download.jpg")

# Set the CSS style for the background image
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url({bg_image});
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

st.title("File Analysis App")
st.write("Upload a file (CSV, TXT, PDF) for analysis.")

# File uploader
uploaded_file = st.file_uploader("Choose a file", type=["csv", "txt", "pdf"])

if uploaded_file is not None:
    # Analyze based on file type
    file_type = uploaded_file.type
    analysis_results = None
    
    if file_type == "text/csv":
        analysis_results = analyze_csv(uploaded_file)
        st.subheader("CSV Analysis Results")
    elif file_type == "text/plain":
        analysis_results = analyze_txt(uploaded_file)
        st.subheader("TXT Analysis Results")
    elif file_type == "application/pdf":
        analysis_results = analyze_pdf(uploaded_file)
        st.subheader("PDF Analysis Results")
    else:
        st.error("Unsupported file type.")

    if analysis_results:
        st.write(analysis_results)

        # Question-answering section
        st.subheader("Ask a question about the file:")
        question = st.text_input("Question:")

        if question:
            context = analysis_results["Content"]  # Assuming 'Content' is available in the analysis_results
            answer = answer_question(question, context)
            st.write(f"Answer: {answer}")
