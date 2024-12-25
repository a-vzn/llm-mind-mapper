import streamlit as st
import streamlit.components.v1 as components
import os
import subprocess
import requests
import json

from llm_mind_mapper.mind_mapper import MindMapper
from llm_mind_mapper.conversation_mapper_llm_client import ConversationMapperLLMClient
from llm_mind_mapper.config import load_config
from langchain_ollama import OllamaLLM

# Load configuration
config = load_config()

def check_ollama_server():
    """Check if Ollama server is running and accessible."""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False

def get_available_models():
    """Get list of available Ollama models."""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json()
            # Extract model names from the response
            model_names = [model['name'] for model in models['models']]
            return sorted(model_names) if model_names else ["llama3.1"]
    except Exception as e:
        st.warning(f"Could not fetch models: {str(e)}")
    return ["llama3.1"]  # Default fallback

# Title of the app
st.title("Conversation Mind Mapper")
st.write("Generate interactive mind maps from conversation transcripts using LLMs")

# Check Ollama server status
if not check_ollama_server():
    st.error("""
        ⚠️ Ollama server is not running. Please follow these steps:
        
        1. Install Ollama if you haven't already:
           ```bash
           curl https://ollama.ai/install.sh | sh
           ```
        
        2. Start the Ollama server:
           ```bash
           ollama serve
           ```
        
        3. In a new terminal, pull the required model:
           ```bash
           ollama pull llama3.1
           ```
        
        After completing these steps, refresh this page.
    """)
    st.stop()

# Sidebar configuration
st.sidebar.title("Configuration")

# Get available models and create dropdown
available_models = get_available_models()
default_model_index = available_models.index(config.llm_model) if config.llm_model in available_models else 0
model_name = st.sidebar.selectbox(
    "Select LLM Model",
    available_models,
    index=default_model_index,
    help="Choose the Ollama model to use for analysis"
)

# Add a button to pull new models
if st.sidebar.button("Pull New Model"):
    model_to_pull = st.sidebar.text_input("Enter model name to pull (e.g., llama2:13b)")
    if model_to_pull:
        try:
            with st.spinner(f"Pulling model {model_to_pull}..."):
                result = requests.post(
                    "http://localhost:11434/api/pull",
                    json={"name": model_to_pull}
                )
                if result.status_code == 200:
                    st.success(f"Successfully pulled model: {model_to_pull}")
                    st.rerun()
                else:
                    st.error(f"Failed to pull model: {result.text}")
        except Exception as e:
            st.error(f"Error pulling model: {str(e)}")

output_filename = st.sidebar.text_input("Output Filename", value=config.default_map_filename)

# Text area to input the conversation transcript
transcript = st.text_area("Enter the conversation transcript:")

# Initialize LLM and process the transcript
if transcript:
    try:
        with st.spinner("Initializing LLM..."):
            llm = OllamaLLM(model=model_name)
            
        with st.spinner("Analyzing conversation and generating mind map..."):
            # Create the mind map
            client = ConversationMapperLLMClient(conversation=transcript, llm=llm)
            conversation_map = client.map_conversation()
            mind_mapper = MindMapper(conversation_map, config=config)
            
            # Save the mind map
            mind_mapper.save(output_filename)
            
            # Display the mind map
            output_path = os.path.join(config.output_dir, output_filename)
            with open(output_path, "r") as file:
                html_content = file.read()
            components.html(html_content, height=750, scrolling=True)
            
            # Display statistics
            st.sidebar.markdown("## Statistics")
            st.sidebar.markdown(f"Number of concepts: {len(mind_mapper.nodes)}")
            st.sidebar.markdown(f"Number of relationships: {len(mind_mapper.edges)}")
            if mind_mapper.rejected_edges:
                st.sidebar.markdown(f"Number of rejected relationships: {len(mind_mapper.rejected_edges)}")
                
    except Exception as e:
        st.error(f"""
            An error occurred: {str(e)}
            
            If this is a connection error, please make sure:
            1. Ollama is installed and running
            2. The selected model ({model_name}) is available
            
            You can install a model using:
            ```bash
            ollama pull {model_name}
            ```
        """)
else:
    st.info("Enter a conversation transcript to generate a mind map")