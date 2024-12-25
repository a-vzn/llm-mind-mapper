from typing import Dict, List, Tuple

from pyvis.network import Network
from langchain_ollama import OllamaLLM

from conversation_result import ConversationResult

class MindMapper(Network):
    def __init__(self, conversation_map: ConversationResult):
        super().__init__(directed=True)
        self.nodes = conversation_map.concepts
        self.edges = conversation_map.relationships
        self.rejected_edges = []
        self.network = Network(height="750px", width="100%")
        self._initialize_graph()

    def _initialize_graph(self):
        for node_label, node_description in self.nodes.items():
            self.add_mm_node(label=node_label, description=node_description)

        for edge in self.edges:
            self.add_mm_edge(edge[0], edge[1])

    def add_mm_node(self, label, description):
        self.network.add_node(hash(label), label=label, title=description)
    
    def add_mm_edge(self, source, target):
        if source not in self.nodes or target not in self.nodes:
            self.rejected_edges.append((source, target))
        else:
            self.network.add_edge(hash(source), hash(target))