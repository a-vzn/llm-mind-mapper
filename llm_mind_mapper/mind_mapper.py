from typing import Dict, List, Tuple, Optional
import logging
import os

from pyvis.network import Network
from langchain_ollama import OllamaLLM

from .conversation_result import ConversationResult
from .config import MindMapperConfig, load_config

# Configure logging
logger = logging.getLogger(__name__)

class MindMapper(Network):
    def __init__(self, conversation_map: ConversationResult, config: Optional[MindMapperConfig] = None):
        super().__init__(directed=True)
        self.config = config or load_config()
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format=self.config.log_format
        )
        
        logger.info("Initializing MindMapper with conversation map")
        self.nodes = conversation_map.concepts
        self.edges = conversation_map.relationships
        self.rejected_edges = []
        self.network = Network(
            height=self.config.network_height,
            width=self.config.network_width
        )
        self._initialize_graph()
        logger.info(f"Initialized graph with {len(self.nodes)} nodes and {len(self.edges)} edges")

    def _initialize_graph(self):
        logger.debug("Starting graph initialization")
        for node_label, node_description in self.nodes.items():
            self.add_mm_node(label=node_label, description=node_description)

        for edge in self.edges:
            self.add_mm_edge(edge[0], edge[1])
        logger.debug("Completed graph initialization")

    def add_mm_node(self, label: str, description: str):
        logger.debug(f"Adding node: {label}")
        self.network.add_node(hash(label), label=label, title=description)
    
    def add_mm_edge(self, source: str, target: str):
        if source not in self.nodes or target not in self.nodes:
            logger.warning(f"Rejected edge: {source} -> {target} (nodes not found)")
            self.rejected_edges.append((source, target))
        else:
            logger.debug(f"Adding edge: {source} -> {target}")
            self.network.add_edge(hash(source), hash(target))
            
    def save(self, filename: Optional[str] = None):
        """Save the mind map to an HTML file."""
        if filename is None:
            filename = self.config.default_map_filename
            
        # Ensure output directory exists
        os.makedirs(self.config.output_dir, exist_ok=True)
        output_path = os.path.join(self.config.output_dir, filename)
        
        logger.info(f"Saving mind map to {output_path}")
        self.network.write_html(output_path)