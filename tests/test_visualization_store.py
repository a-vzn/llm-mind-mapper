import os
import json
import shutil
import pytest
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

@dataclass
class ConversationResult:
    concepts: Dict[str, str]
    relationships: List[Tuple[str, str]]

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
        from datetime import datetime
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

@pytest.fixture
def test_storage_dir(tmp_path):
    """Create a temporary directory for test storage."""
    test_dir = tmp_path / "test_visualizations"
    yield test_dir
    # Cleanup after tests
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)

@pytest.fixture
def store(test_storage_dir):
    """Create a VisualizationStore instance for testing."""
    return VisualizationStore(storage_dir=str(test_storage_dir))

@pytest.fixture
def sample_conversation_result():
    """Create a sample ConversationResult for testing."""
    return ConversationResult(
        concepts={
            "Python": "A programming language",
            "Testing": "Process of validating code"
        },
        relationships=[
            ("Python", "Testing")
        ]
    )

def test_store_initialization(test_storage_dir):
    """Test that store initialization creates necessary directories and files."""
    store = VisualizationStore(storage_dir=str(test_storage_dir))
    
    # Check if directory was created
    assert os.path.exists(test_storage_dir)
    
    # Check if metadata file was created
    metadata_path = os.path.join(test_storage_dir, "metadata.json")
    assert os.path.exists(metadata_path)
    
    # Check if metadata file has correct initial content
    with open(metadata_path, "r") as f:
        metadata = json.load(f)
        assert isinstance(metadata, list)
        assert len(metadata) == 0

def test_store_visualization(store, sample_conversation_result):
    """Test storing a new visualization."""
    transcript = "This is a test conversation"
    html_content = "<html>Test visualization</html>"
    
    # Store visualization
    viz = store.store_visualization(transcript, sample_conversation_result, html_content)
    
    # Check if visualization was stored correctly
    assert viz.transcript == transcript
    assert viz.conversation_result == sample_conversation_result
    assert os.path.exists(viz.html_path)
    
    # Check if files were created
    viz_dir = os.path.join(store.storage_dir, viz.id)
    assert os.path.exists(os.path.join(viz_dir, "transcript.txt"))
    assert os.path.exists(os.path.join(viz_dir, "visualization.html"))
    assert os.path.exists(os.path.join(viz_dir, "result.json"))
    
    # Check metadata was updated
    metadata_path = os.path.join(store.storage_dir, "metadata.json")
    with open(metadata_path, "r") as f:
        metadata = json.load(f)
        assert len(metadata) == 1
        assert metadata[0]["id"] == viz.id

def test_get_visualization(store, sample_conversation_result):
    """Test retrieving a stored visualization."""
    # Store a visualization first
    transcript = "Test conversation"
    html_content = "<html>Test</html>"
    stored_viz = store.store_visualization(transcript, sample_conversation_result, html_content)
    
    # Retrieve the visualization
    retrieved_viz = store.get_visualization(stored_viz.id)
    
    # Check if retrieved visualization matches stored one
    assert retrieved_viz is not None
    assert retrieved_viz.id == stored_viz.id
    assert retrieved_viz.transcript == stored_viz.transcript
    assert retrieved_viz.conversation_result.concepts == stored_viz.conversation_result.concepts
    assert set(map(tuple, retrieved_viz.conversation_result.relationships)) == set(map(tuple, stored_viz.conversation_result.relationships))

def test_get_all_visualizations(store, sample_conversation_result):
    """Test retrieving all stored visualizations."""
    # Store multiple visualizations
    transcripts = ["First conversation", "Second conversation"]
    html_content = "<html>Test</html>"
    
    stored_vizs = []
    for transcript in transcripts:
        viz = store.store_visualization(transcript, sample_conversation_result, html_content)
        stored_vizs.append(viz)
    
    # Retrieve all visualizations
    all_vizs = store.get_all_visualizations()
    
    # Check if all visualizations were retrieved
    assert len(all_vizs) == len(transcripts)
    assert all(isinstance(viz, StoredVisualization) for viz in all_vizs)
    
    # Check if visualizations are sorted by timestamp (newest first)
    timestamps = [viz.timestamp for viz in all_vizs]
    assert timestamps == sorted(timestamps, reverse=True)

def test_nonexistent_visualization(store):
    """Test attempting to retrieve a non-existent visualization."""
    viz = store.get_visualization("nonexistent-id")
    assert viz is None

def test_duplicate_storage(store, sample_conversation_result):
    """Test storing the same content multiple times creates unique entries."""
    transcript = "Test conversation"
    html_content = "<html>Test</html>"
    
    # Store same content twice
    viz1 = store.store_visualization(transcript, sample_conversation_result, html_content)
    viz2 = store.store_visualization(transcript, sample_conversation_result, html_content)
    
    # Check that they have different IDs
    assert viz1.id != viz2.id
    
    # Check that both are retrievable
    assert store.get_visualization(viz1.id) is not None
    assert store.get_visualization(viz2.id) is not None 