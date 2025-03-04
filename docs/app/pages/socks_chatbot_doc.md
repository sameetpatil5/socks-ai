# SocksAI Chatbot Page Documentation

## Overview

The `socks_chatbot.py` file is a Streamlit page for interacting with `SocksAI`, an AI-powered chatbot designed to assist users with stock market analysis, financial insights, and market trends. Users can also extend the chatbot’s knowledge base by adding external documents.

## Libraries and Tools Used

The following libraries and tools are utilized in the project:

- **streamlit**: Web framework for UI interactions.
- **logging**: For tracking chatbot activity and errors.
- **pathlib**: For handling file paths when uploading knowledge sources.
- **urllib.parse**: For validating URLs.
- **streamlit_components**: Custom UI enhancements like buttons and toast notifications.

## Page Configuration

The page is configured with a centered layout and expanded sidebar:

```python
st.set_page_config(
    page_title="SocksAI",
    page_icon=":socks:",
    layout="centered",
    initial_sidebar_state="expanded",
)
```

## Workflow

### 1. Chatbot Interaction

Users can enter prompts to interact with the chatbot. The conversation history is stored in session state:

```python
if prompt := st.chat_input(placeholder="Talk to SocksAI..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    
    st.session_state["chatbot_interactions"].append({"role": "user", "content": prompt})
    
    with st.spinner("Thinking..."):
        with st.chat_message("assistant"):
            response = st.session_state.scba.chat(prompt)
            full_response = st.write_stream(response)
    
    st.session_state["chatbot_interactions"].append({"role": "assistant", "content": full_response})
```

### 2. Adding Knowledge to the Chatbot

Users can add additional knowledge sources to enhance chatbot responses.

#### URL Validation

Validates whether the provided URL is correctly formatted:

```python
def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False
```

#### Adding External Knowledge

Users can add knowledge sources from a website, a PDF URL, or a locally uploaded PDF:

```python
@st.dialog("Add Knowledge", width="large")
def add_knowledge():
    knowledge_type = st.selectbox("Select Knowledge Type", ["Website", "PDF URL", "Local PDF"], key="knowledge_type")
    
    if knowledge_type in ["Website", "PDF URL"]:
        knowledge_url = st.text_input("Enter the URL", key="knowledge_url")
        if st.button("Add") and is_valid_url(knowledge_url):
            st.session_state.scba.add_knowledge(knowledge_url, knowledge_type.lower())
            show_toast("✅ Knowledge added successfully!")
```

#### Uploading Local PDFs

Users can upload a local PDF to store knowledge temporarily:

```python
elif knowledge_type == "Local PDF":
    knowledge_file = st.file_uploader("Upload a PDF", type=["pdf"], key="knowledge_pdf_uploader_key")
    
    if knowledge_file:
        knowledge_data_dir = Path("data/knowledge_pdfs")
        knowledge_data_dir.mkdir(parents=True, exist_ok=True)
        knowledge_file_path = knowledge_data_dir / knowledge_file.name
        
        with open(knowledge_file_path, mode="wb") as pdf:
            pdf.write(knowledge_file.getbuffer())
        
        show_toast("✅ Knowledge added successfully!")
```

## UI Components

### Chat Interface

Displays the chatbot conversation history and input field:

```python
st.title("SocksAI Chatbot")
for message in st.session_state["chatbot_interactions"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
```

### Adding Knowledge

A button for adding knowledge sources dynamically:

```python
st.button("Add Knowledge", on_click=add_knowledge, key="add_knowledge")
```

## Example Usage

### Running the App

To launch the Streamlit app, run:

```bash
streamlit run app.py
```

### Asking a Question

```python
response = st.session_state.scba.chat("What is the current price of TSLA?")
for chunk in response:
    print(chunk)
```

### Adding Knowledge from a Website

```python
st.session_state.scba.add_knowledge("https://www.nasdaq.com", "website")
```

## Conclusion

The `SocksAI Chatbot` page enables users to interact with an AI-powered financial assistant, enhancing responses with real-time stock analysis and additional knowledge sources. It provides an intuitive UI for dynamic knowledge expansion and seamless conversations.
