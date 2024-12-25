# LLM Mind Mapper

A Python tool that uses Large Language Models to analyze conversations and create interactive mind maps. The tool processes conversation transcripts and generates visual representations of concepts and their relationships.

## Features

- Process conversation transcripts using LLMs
- Generate interactive mind maps using PyVis
- Web interface built with Streamlit
- Visualize relationships between concepts
- Export mind maps as HTML
- Configurable settings through a central configuration system
- Comprehensive logging system

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/llm-mind-mapper.git
cd llm-mind-mapper

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package in development mode
pip install -e .
```

## Usage

### Running the Streamlit App

```bash
streamlit run streamlit_app.py
```

This will start the web interface where you can:
1. Enter conversation transcripts
2. Configure LLM model and output settings
3. Generate and view interactive mind maps
4. See statistics about the generated map

### Using as a Python Package

```python
from llm_mind_mapper import MindMapper, ConversationMapperLLMClient, MindMapperConfig
from langchain_ollama import OllamaLLM

# Initialize the LLM
llm = OllamaLLM(model="llama3.1")

# Optional: Configure settings
config = MindMapperConfig(
    network_height="750px",
    network_width="100%",
    llm_model="llama3.1",
    log_level="INFO",
    output_dir="./output",
    default_map_filename="conversation_map.html"
)

# Create a conversation mapper
client = ConversationMapperLLMClient(conversation="Your conversation text", llm=llm)
conversation_map = client.map_conversation()

# Generate the mind map with custom config
mind_mapper = MindMapper(conversation_map, config=config)
mind_mapper.save("my_map.html")
```

## Project Structure

```
llm_mind_mapper/
├── __init__.py          # Package initialization and exports
├── mind_mapper.py       # Core mind mapping functionality
├── config.py            # Configuration management
├── conversation_result.py    # Data structures for analysis results
└── conversation_mapper_llm_client.py  # LLM interaction logic
tests/
├── __init__.py
└── test_mind_mapper.py  # Unit tests
streamlit_app.py         # Web interface
setup.py                 # Package installation configuration
README.md               # Documentation
```

### Key Components

- **mind_mapper.py**: Core class for creating and managing mind maps using PyVis
- **config.py**: Configuration management with customizable settings
- **conversation_mapper_llm_client.py**: Handles LLM interaction and conversation analysis
- **conversation_result.py**: Data structures for storing analysis results
- **streamlit_app.py**: Web interface for easy interaction with the tool

## Configuration

The tool can be configured through the `MindMapperConfig` class with the following options:

```python
config = MindMapperConfig(
    network_height="750px",    # Height of the mind map visualization
    network_width="100%",      # Width of the mind map visualization
    llm_model="llama3.1",      # Default LLM model to use
    log_level="INFO",          # Logging level
    output_dir="./output",     # Directory for saving mind maps
    default_map_filename="conversation_map.html"  # Default output filename
)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 