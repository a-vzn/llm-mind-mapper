import streamlit as st
import streamlit.components.v1 as components
from mind_mapper import MindMapper
from langchain_ollama import OllamaLLM
from conversation_mapper_llm_client import ConversationMapperLLMClient

# Title of the app
st.title("Conversation Transcript Analyzer")

# Text area to input the conversation transcript
transcript = st.text_area("Enter the conversation transcript:")

# Placeholder for the HTML embed object
html_placeholder = st.empty()

llm = OllamaLLM(model="llama3.1")

# Display the transcript if provided
if transcript:
    client = ConversationMapperLLMClient(conversation=transcript, llm=llm)
    conversation_map = client.map_conversation()
    mind_mapper = MindMapper(conversation_map,)
    mind_mapper.network.write_html("./conversation_map.html")

    # Example HTML embed object (you can replace this with your actual HTML content)
    with open("./conversation_map.html", "r") as file:
        html_content = file.read()
    components.html(html_content, height=750, scrolling=True)