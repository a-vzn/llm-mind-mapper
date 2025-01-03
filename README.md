# LLM Mind Mapper

A Python tool that uses Large Language Models to analyze conversations and create interactive mind maps. The tool processes conversation transcripts and generates visual representations of concepts and their relationships.

## Prerequisites

### [Pyenv](https://github.com/pyenv/pyenv)
It is recommended to use `pyenv` for managing Python versions. follow [these basic instructions](https://github.com/pyenv/pyenv) to install `pyenv`

```bash
$ pyenv install 3.x.x
```
A minimum python version of 3.8 is required for this application.

### [Ollama](https://ollama.com/)
  ```bash
  # Install Ollama
  https://ollama.com/download

  # Pull default model
  ollama pull llama3.1  

  # Start Ollama server
  ollama serve
  ```

## Tech Stack

- **LLM Integration**: Langchain and Langchain-Ollama
- **Visualization**: PyVis for interactive network graphs
- **Web Interface**: Streamlit
- **Configuration**: Pydantic
- **Core Dependencies**: NetworkX, Pandas, Python-dotenv

## Features

- Process conversation transcripts using LLMs
- Generate interactive mind maps using PyVis
- Web interface built with Streamlit
- Visualize relationships between concepts
- Export mind maps as HTML
- Configurable settings through a central configuration system
- Comprehensive logging system
- Multiple LLM model support through Ollama

## Installation

```bash
# Clone the repository
git clone https://github.com/aviralsomani/llm-mind-mapper.git
cd llm-mind-mapper

# Create a virtual environment (optional but recommended)
pyenv virtualenv llm-mind-mapper
pyenv activate llm-mind-mapper

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
2. Select and configure LLM models
3. Pull new Ollama models as needed
4. Generate and view interactive mind maps
5. See statistics about the generated map
6. Customize output settings

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

### Available Models

The tool supports any model available through Ollama. You can:
1. Use the web interface to select from available models through a dropdown menu
2. Pull new models through the interface using the "Pull New Model" button
3. Manually pull models using the Ollama CLI:
   ```bash
   ollama pull llama3.1    # Default model
   ollama pull llama2      # Alternative model
   ollama pull llama2:13b  # Larger model variant
   ```

## Project Structure

```
.
├── llm_mind_mapper/           # Main package directory
│   ├── __init__.py           # Package initialization and exports
│   ├── mind_mapper.py        # Core mind mapping functionality
│   ├── config.py             # Configuration management
│   ├── conversation_result.py # Data structures for analysis results
│   └── conversation_mapper_llm_client.py  # LLM interaction logic
├── tests/                    # Test directory
│   ├── __init__.py
│   └── test_mind_mapper.py   # Unit tests
├── output/                   # GIT IGNORED - default output directory for mind maps
├── streamlit_app.py         # Web interface
├── setup.py                 # Package installation configuration
├── requirements.txt         # Project dependencies
└── README.md               # Documentation
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.