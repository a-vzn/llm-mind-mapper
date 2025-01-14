import streamlit as st
import streamlit.components.v1 as components
import os
import requests
import json
import glob
from datetime import datetime

from llm_mind_mapper.mind_mapper import MindMapper
from llm_mind_mapper.conversation_mapper_llm_client import ConversationMapperLLMClient
from llm_mind_mapper.config import load_config
from langchain_ollama import OllamaLLM

# Page configuration
st.set_page_config(
    page_title="Conversation Mind Mapper",
    page_icon="🧠",
    layout="wide"
)

# Load configuration
config = load_config()

# Initialize session state
if 'model_pull_requested' not in st.session_state:
    st.session_state.model_pull_requested = False
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'show_previous_maps' not in st.session_state:
    st.session_state.show_previous_maps = False
if 'current_map_html' not in st.session_state:
    st.session_state.current_map_html = None
if 'current_map_path' not in st.session_state:
    st.session_state.current_map_path = None
if 'last_transcript' not in st.session_state:
    st.session_state.last_transcript = None
if 'map_views' not in st.session_state:
    st.session_state.map_views = {}
if 'conversation_views' not in st.session_state:
    st.session_state.conversation_views = {}
if 'show_delete_confirmation' not in st.session_state:
    st.session_state.show_delete_confirmation = False

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
            model_names = [model['name'] for model in models['models']]
            return sorted(model_names) if model_names else ["llama3.1"]
    except Exception as e:
        st.warning(f"Could not fetch models: {str(e)}")
    return ["llama3.1"]  # Default fallback

def pull_model(model_name: str) -> bool:
    """Pull a new model from Ollama."""
    try:
        with st.spinner(f"Pulling model {model_name}..."):
            result = requests.post(
                "http://localhost:11434/api/pull",
                json={"name": model_name}
            )
            return result.status_code == 200
    except Exception as e:
        st.error(f"Error pulling model: {str(e)}")
        return False

def get_previous_mind_maps():
    """Get list of previously generated mind maps."""
    try:
        maps = glob.glob(os.path.join(config.output_dir, "*.html"))
        # Sort by modification time, newest first
        maps.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        return maps
    except Exception:
        return []

def get_conversation_preview(text: str, max_length: int = 200) -> str:
    """Generate a preview of the conversation text."""
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(' ', 1)[0] + "..."

def save_conversation_metadata(output_path: str, conversation: str, model: str):
    """Save conversation metadata alongside the mind map."""
    metadata_path = output_path.replace('.html', '_metadata.json')
    metadata = {
        'conversation': conversation,
        'model': model,
        'timestamp': datetime.now().isoformat()
    }
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f)

def load_conversation_metadata(html_path: str) -> dict:
    """Load conversation metadata for a mind map."""
    metadata_path = html_path.replace('.html', '_metadata.json')
    try:
        with open(metadata_path, 'r') as f:
            return json.load(f)
    except Exception:
        return {'conversation': '', 'model': '', 'timestamp': ''}

def format_timestamp(timestamp):
    """Format timestamp into readable date/time."""
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def generate_unique_filename(base_filename: str) -> str:
    """Generate a unique filename with timestamp."""
    # Remove .html extension if present
    base_name = base_filename.replace('.html', '')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{base_name}_{timestamp}.html"

def toggle_map_view(map_name: str):
    """Toggle the view state of a map."""
    if map_name not in st.session_state.map_views:
        st.session_state.map_views[map_name] = False
    st.session_state.map_views[map_name] = not st.session_state.map_views[map_name]

def toggle_conversation_view(map_name: str):
    """Toggle the view state of a conversation."""
    if map_name not in st.session_state.conversation_views:
        st.session_state.conversation_views[map_name] = False
    st.session_state.conversation_views[map_name] = not st.session_state.conversation_views[map_name]

def delete_all_maps():
    """Delete all mind maps and their metadata."""
    try:
        maps = get_previous_mind_maps()
        for map_path in maps:
            os.remove(map_path)
            metadata_path = map_path.replace('.html', '_metadata.json')
            if os.path.exists(metadata_path):
                os.remove(metadata_path)
        
        # Clear all view states
        st.session_state.map_views = {}
        st.session_state.conversation_views = {}
        st.session_state.show_delete_confirmation = False
        return True
    except Exception as e:
        st.error(f"Error deleting maps: {str(e)}")
        return False

# Main layout
st.title("🧠 Conversation Mind Mapper")
st.markdown("""
Generate interactive mind maps from conversation transcripts using LLMs.
This tool helps visualize concepts and their relationships from text.
""")

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
with st.sidebar:
    st.title("⚙️ Configuration")
    
    # Model selection
    st.subheader("Model Settings")
    available_models = get_available_models()
    default_model_index = available_models.index(config.llm_model) if config.llm_model in available_models else 0
    model_name = st.selectbox(
        "Select LLM Model",
        available_models,
        index=default_model_index,
        help="Choose the Ollama model to use for analysis"
    )
    
    # Model pulling interface
    st.subheader("Add New Model")
    if st.button("Pull New Model"):
        st.session_state.model_pull_requested = True
    
    if st.session_state.model_pull_requested:
        model_to_pull = st.text_input(
            "Enter model name",
            placeholder="e.g., llama2:13b",
            help="Enter the name of the model you want to pull from Ollama"
        )
        if model_to_pull:
            if pull_model(model_to_pull):
                st.success(f"Successfully pulled model: {model_to_pull}")
                st.session_state.model_pull_requested = False
                st.rerun()
    
    # Output settings
    st.subheader("Output Settings")
    output_filename = st.text_input(
        "Output Filename",
        value=config.default_map_filename,
        help="Name of the output HTML file (must end with .html)"
    )
    
    # Ensure filename ends with .html
    if not output_filename.endswith('.html'):
        output_filename += '.html'
    
    # Display statistics if available
    if 'mind_mapper' in st.session_state:
        st.subheader("📊 Statistics")
        mapper = st.session_state.mind_mapper
        st.metric("Number of concepts", len(mapper.nodes))
        st.metric("Number of relationships", len(mapper.edges))
        if mapper.rejected_edges:
            st.metric("Rejected relationships", len(mapper.rejected_edges))

# Main content area
tab1, tab2 = st.tabs(["📝 Create New Map", "📚 Previous Maps"])

with tab1:
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📝 Input")
        # Add a form to handle command+enter properly
        with st.form(key="transcript_form"):
            transcript = st.text_area(
                "Enter conversation transcript",
                height=200,
                placeholder="Paste your conversation text here...",
                help="Enter the conversation text you want to analyze",
                key="transcript_input"
            )
            
            # Add Generate button inside the form
            generate_button = st.form_submit_button(
                "🚀 Generate Mind Map",
                help="Click to generate the mind map from your conversation",
                type="primary",
                use_container_width=True
            )
            
            st.markdown("""
            <div style="padding: 8px;">
            <small>💡 Tip: Press Ctrl/Cmd + Enter in the text area to generate</small>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.subheader("ℹ️ Tips")
        st.markdown("""
        - Longer conversations will generate more detailed maps
        - Make sure the text is clear and well-formatted
        - The analysis may take a few moments for longer texts
        - You can drag nodes to rearrange the visualization
        """)

    # Display the generated map in the first tab
    if st.session_state.current_map_html:
        st.subheader("🗺️ Generated Mind Map")
        components.html(st.session_state.current_map_html, height=750, scrolling=True)

with tab2:
    st.subheader("📚 Previous Mind Maps")
    # Force refresh of previous maps list
    previous_maps = get_previous_mind_maps()
    
    if not previous_maps:
        st.info("No previous mind maps found. Generate your first map in the 'Create New Map' tab!")
    else:
        # Header with map count and delete all button
        header_col1, header_col2, header_col3 = st.columns([4, 2, 1])
        with header_col1:
            st.write(f"Found {len(previous_maps)} previous mind maps")
        with header_col2:
            if not st.session_state.show_delete_confirmation:
                if st.button("🗑️ Delete All Maps", type="secondary", help="Delete all saved mind maps", use_container_width=True):
                    st.session_state.show_delete_confirmation = True
                    st.rerun()
        
        # Show confirmation dialog if delete all was clicked
        if st.session_state.show_delete_confirmation:
            st.warning("⚠️ Are you sure you want to delete all mind maps? This action cannot be undone.")
            confirm_col1, confirm_col2 = st.columns([1, 1])
            with confirm_col1:
                if st.button("✅ Yes, Delete All", type="primary", use_container_width=True):
                    if delete_all_maps():
                        st.success("✅ All mind maps deleted successfully!")
                        st.rerun()
            with confirm_col2:
                if st.button("❌ Cancel", type="secondary", use_container_width=True):
                    st.session_state.show_delete_confirmation = False
                    st.rerun()
            st.markdown("---")  # Add a separator
        
        # Create a container for the maps list
        maps_container = st.container()
        
        with maps_container:
            for map_path in previous_maps:
                map_name = os.path.basename(map_path)
                metadata = load_conversation_metadata(map_path)
                conversation_preview = get_conversation_preview(metadata.get('conversation', ''))
                model_used = metadata.get('model', 'unknown model')
                
                # Create a descriptive title
                title = f"🗺️ Mind Map: {conversation_preview}"
                
                # Create an expander for each map
                with st.expander(title):
                    # Show metadata
                    st.caption(f"Generated with {model_used} on {format_timestamp(os.path.getmtime(map_path))}")
                    
                    # Create three columns for the controls
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        # Initialize view state if needed
                        if map_name not in st.session_state.map_views:
                            st.session_state.map_views[map_name] = False
                        
                        # Toggle button with current state
                        is_visible = st.session_state.map_views[map_name]
                        if st.button(
                            "❌ Hide Map" if is_visible else "👁️ View Map",
                            key=f"toggle_{map_name}",
                            type="primary" if not is_visible else "secondary"
                        ):
                            toggle_map_view(map_name)
                            st.rerun()
                    
                    with col2:
                        # Initialize conversation view state if needed
                        if map_name not in st.session_state.conversation_views:
                            st.session_state.conversation_views[map_name] = False
                        
                        # Toggle button with current state
                        is_conv_visible = st.session_state.conversation_views[map_name]
                        if st.button(
                            "❌ Hide Conversation" if is_conv_visible else "💬 Show Conversation",
                            key=f"conv_{map_name}",
                            type="primary" if not is_conv_visible else "secondary"
                        ):
                            toggle_conversation_view(map_name)
                            st.rerun()
                    
                    with col3:
                        # Delete button
                        if st.button("🗑️ Delete", key=f"delete_{map_name}", type="secondary"):
                            try:
                                # Delete both HTML and metadata files
                                os.remove(map_path)
                                metadata_path = map_path.replace('.html', '_metadata.json')
                                if os.path.exists(metadata_path):
                                    os.remove(metadata_path)
                                # Clear both view states for this map
                                if map_name in st.session_state.map_views:
                                    del st.session_state.map_views[map_name]
                                if map_name in st.session_state.conversation_views:
                                    del st.session_state.conversation_views[map_name]
                                st.success(f"Deleted {map_name}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error deleting {map_name}: {str(e)}")
                    
                    # Show conversation if toggled (full width)
                    if st.session_state.conversation_views.get(map_name, False):
                        st.markdown("**Original Conversation:**")
                        st.markdown(
                            f"""<div style="max-height: 200px; overflow-y: auto; padding: 15px; 
                            border: 1px solid rgba(49, 51, 63, 0.2); border-radius: 5px; margin: 10px 0; 
                            background-color: transparent; width: 100%; color: inherit;">
                            {metadata.get('conversation', 'Conversation not available').replace(chr(10), '<br>')}
                            </div>""",
                            unsafe_allow_html=True
                        )
                    
                    # Show the map if view is toggled
                    if st.session_state.map_views.get(map_name, False):
                        with open(map_path, "r") as file:
                            html_content = file.read()
                        components.html(html_content, height=750, scrolling=True)

# Process the transcript only when Generate button is clicked
if transcript and generate_button:
    # Reset processing state if new text is submitted
    if st.session_state.last_transcript != transcript:
        st.session_state.processing = False
        st.session_state.last_transcript = transcript
    
    if not st.session_state.processing:
        try:
            st.session_state.processing = True
            
            with st.spinner("🤖 Initializing LLM..."):
                llm = OllamaLLM(model=model_name)
            
            with st.spinner("🔄 Analyzing conversation and generating mind map..."):
                client = ConversationMapperLLMClient(conversation=transcript, llm=llm)
                conversation_map = client.map_conversation()
                mind_mapper = MindMapper(conversation_map, config=config)
                st.session_state.mind_mapper = mind_mapper
                
                # Generate unique filename
                unique_filename = generate_unique_filename(output_filename)
                output_path = os.path.join(config.output_dir, unique_filename)
                
                # Save the mind map and metadata
                mind_mapper.save(unique_filename)
                save_conversation_metadata(output_path, transcript, model_name)
                
                # Read and store the generated map
                with open(output_path, "r") as file:
                    html_content = file.read()
                    st.session_state.current_map_html = html_content
                    st.session_state.current_map_path = output_path
                
                st.success("✅ Mind map generated successfully!")
                # Force a rerun to update the UI with the new map
                st.rerun()
            
            st.session_state.processing = False
            
        except Exception as e:
            st.session_state.processing = False
            st.error(f"""
                ❌ An error occurred: {str(e)}
                
                If this is a connection error, please make sure:
                1. Ollama is installed and running
                2. The selected model ({model_name}) is available
                
                You can install a model using:
                ```bash
                ollama pull {model_name}
                ```
            """)
elif not transcript:
    st.info("👆 Enter a conversation transcript above to generate a mind map")