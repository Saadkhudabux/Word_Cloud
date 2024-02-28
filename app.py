import pandas as pd
import streamlit as st
from wordcloud import WordCloud, STOPWORDS
import PyPDF2
from docx import Document
import base64
from io import BytesIO
import matplotlib.pyplot as plt
from collections import Counter

# Function for file reading
def read_text(file):
    if file.name.endswith('.pdf'):
        pdfReader = PyPDF2.PdfReader(file)
        text = ''
        for page in range(len(pdfReader.pages)):
            text += pdfReader.pages[page].extract_text()  # Changed method name to extract_text
    elif file.name.endswith('.docx'):
        doc = Document(file)
        text = ''
        for para in doc.paragraphs:
            text += para.text
    return text

# Function to filter out stopwords
def filter_stopwords(text, additional_stopwords=[]):
    words = text.split()
    stopwords = STOPWORDS.union(set(additional_stopwords))
    filtered_words = [word for word in words if word.lower() not in stopwords]
    return ' '.join(filtered_words)

# Function to create download link for plot
def get_image_download_link(fig, filename, text):
    buffered = BytesIO()
    fig.savefig(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a href="data:image/png;base64,{img_str}" download="{filename}.png">{text}</a>'
    return href

# Streamlit code
st.title('Word Cloud App')
st.subheader('Upload a .pdf or .docx file to generate a word cloud')

file = st.file_uploader('Upload file', type=['pdf', 'docx', 'txt'])
st.set_option('deprecation.showfileUploaderEncoding', False)

if file:
    file_details = {'FileName': file.name, 'FileType': file.type, 'FileSize': file.size}
    st.write(file_details)
    
    # check the file type and read the text
    if file.type == "text/plain":
        text = file.read()
        text = text.decode("utf-8")
    elif file.type == "application/pdf":
        text = read_text(file)
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        text = read_text(file)
    else:
        st.error('File type not supported')
        st.stop()
    
    # Side bar check box and multiselect box for stopwords
    use_standard_stopwords = st.sidebar.checkbox('Stopwords', True)
    top_words = st.sidebar.multiselect('Select top words to remove', ['said', 'mr', 'mrs', 'one', 'two', 'three', 'also', 'say', 
                                                                     'said', 'would', 'could', 'us', 'may', 'might', 'shall', 'must', 
                                                                     'need', 'know', 'go', 'get', 'like', 'see', 'tell', 'think', 'come', 
                                                                     'take'])
    additional_stopwords = st.sidebar.multiselect('Select additional stopwords:', top_words)

    if use_standard_stopwords:
        text = filter_stopwords(text, additional_stopwords)
    else:
        text = filter_stopwords(text, additional_stopwords)
  
    # Word count table
    words = text.split()
    word_count = Counter(words)
    word_count_df = pd.DataFrame(word_count.items(), columns=['Word', 'Count'])
    st.subheader('Word Count Table')
    st.write(word_count_df)

    # Generate word cloud  
    wordcloud = WordCloud().generate(text)
    fig = plt.figure(figsize=(10, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')

    # Save plot functionality
    format = st.selectbox('Select file format', ['png', 'jpg', 'svg', 'pdf'])
    resolution = st.slider('Select resolution', 50, 300, 100)

    if st.button(f"Save as {format}"):
        plt.savefig(f"wordcloud.{format}", format=format, dpi=resolution)
        st.markdown(get_image_download_link(fig, 'wordcloud', f"Click here to download the word cloud as a {format} file"), unsafe_allow_html=True)
    
    # Display word cloud plot
    st.subheader('Word Cloud Plot')
    st.pyplot(fig)

# word count table at the bottom
st.sidebar.markdown("-------")
st.sidebar.subheader('Give me a Thumbs Up if you like this app')

# add author name and info
st.sidebar.markdown("Created by: [Saad khuda bux](https://www.linkedin.com/in/saad-khuda-bux-32a827294/)")
