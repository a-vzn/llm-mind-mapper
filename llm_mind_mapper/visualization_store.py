import os
import json
from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional
from .conversation_result import ConversationResult

@dataclass
class StoredVisualization:
    id: str
    timestamp: str
    transcript: str
    conversation_result: ConversationResult
    html_path: str

class VisualizationStore:
    def __init__(self, storage_dir: str = "visualizations"):
        self.storage_dir = storage_dir
        self._ensure_storage_exists()
        
    def _ensure_storage_exists(self):
        """Ensure storage directory and metadata file exist."""
        os.makedirs(self.storage_dir, exist_ok=True)
        metadata_path = os.path.join(self.storage_dir, "metadata.json")
        if not os.path.exists(metadata_path):
            with open(metadata_path, "w") as f:
                json.dump([], f)

    def store_visualization(self, transcript: str, conversation_result: ConversationResult, html_content: str) -> StoredVisualization:
        """Store a new visualization."""
        # Generate unique ID using timestamp
        timestamp = datetime.now().isoformat()
        viz_id = timestamp.replace(":", "-").replace(".", "-")
        
        # Create visualization directory
        viz_dir = os.path.join(self.storage_dir, viz_id)
        os.makedirs(viz_dir, exist_ok=True)
        
        # Save HTML file
        html_path = os.path.join(viz_dir, "visualization.html")
        with open(html_path, "w") as f:
            f.write(html_content)
        
        # Save transcript
        with open(os.path.join(viz_dir, "transcript.txt"), "w") as f:
            f.write(transcript)
        
        # Save conversation result
        with open(os.path.join(viz_dir, "result.json"), "w") as f:
            json.dump({
                "concepts": conversation_result.concepts,
                "relationships": conversation_result.relationships
            }, f, indent=2)
        
        # Create visualization object
        visualization = StoredVisualization(
            id=viz_id,
            timestamp=timestamp,
            transcript=transcript,
            conversation_result=conversation_result,
            html_path=html_path
        )
        
        # Update metadata
        self._update_metadata(visualization)
        
        return visualization
    
    def _update_metadata(self, visualization: StoredVisualization):
        """Update metadata file with new visualization."""
        metadata_path = os.path.join(self.storage_dir, "metadata.json")
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
        
        metadata.append({
            "id": visualization.id,
            "timestamp": visualization.timestamp
        })
        
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
    
    def get_all_visualizations(self) -> List[StoredVisualization]:
        """Retrieve all stored visualizations."""
        metadata_path = os.path.join(self.storage_dir, "metadata.json")
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
        
        visualizations = []
        for entry in metadata:
            viz = self.get_visualization(entry["id"])
            if viz:
                visualizations.append(viz)
        
        return sorted(visualizations, key=lambda x: x.timestamp, reverse=True)
    
    def get_visualization(self, viz_id: str) -> Optional[StoredVisualization]:
        """Retrieve a specific visualization by ID."""
        viz_dir = os.path.join(self.storage_dir, viz_id)
        if not os.path.exists(viz_dir):
            return None
        
        # Load transcript
        with open(os.path.join(viz_dir, "transcript.txt"), "r") as f:
            transcript = f.read()
        
        # Load conversation result
        with open(os.path.join(viz_dir, "result.json"), "r") as f:
            result_data = json.load(f)
            conversation_result = ConversationResult(
                concepts=result_data["concepts"],
                relationships=result_data["relationships"]
            )
        
        html_path = os.path.join(viz_dir, "visualization.html")
        
        return StoredVisualization(
            id=viz_id,
            timestamp=viz_id,  # Using ID as timestamp since it's derived from it
            transcript=transcript,
            conversation_result=conversation_result,
            html_path=html_path
        ) 