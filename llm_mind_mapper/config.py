from dataclasses import dataclass
from typing import Optional

@dataclass
class MindMapperConfig:
    """Configuration for the MindMapper application."""
    
    # Network visualization settings
    network_height: str = "750px"
    network_width: str = "100%"
    
    # LLM settings
    llm_model: str = "llama3.1"
    
    # Logging settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Output settings
    output_dir: str = "./output"
    default_map_filename: str = "conversation_map.html"

def load_config(config_path: Optional[str] = None) -> MindMapperConfig:
    """Load configuration from a file or return default configuration."""
    if config_path is None:
        return MindMapperConfig()
    
    # TODO: Implement config file loading
    return MindMapperConfig() 