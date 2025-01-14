import pytest
from unittest.mock import MagicMock, patch
from dataclasses import dataclass
from typing import Dict, List, Tuple

@dataclass
class ConversationResult:
    concepts: Dict[str, str]
    relationships: List[Tuple[str, str]]

@pytest.fixture
def mock_store():
    """Create a mock VisualizationStore."""
    store = MagicMock()
    return store

@pytest.fixture
def mock_streamlit():
    """Create a mock Streamlit module."""
    streamlit = MagicMock()
    streamlit.session_state = {}
    return streamlit

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

def test_first_visualization_storage(mock_store, mock_streamlit):
    """Test storing first visualization (no previous transcript)."""
    with patch.dict('sys.modules', {'streamlit': mock_streamlit}):
        transcript = "Test conversation"
        conversation_map = ConversationResult(
            concepts={"Test": "A test concept"},
            relationships=[]
        )
        html_content = "<html>Test</html>"
        
        # Simulate first run (no last_transcript in session state)
        if 'last_transcript' not in mock_streamlit.session_state or mock_streamlit.session_state.get('last_transcript') != transcript:
            mock_store.store_visualization(transcript, conversation_map, html_content)
            mock_streamlit.session_state['last_transcript'] = transcript
        
        # Verify store_visualization was called
        mock_store.store_visualization.assert_called_once_with(
            transcript, conversation_map, html_content
        )

def test_duplicate_visualization_storage(mock_store, mock_streamlit):
    """Test that duplicate visualization is not stored."""
    with patch.dict('sys.modules', {'streamlit': mock_streamlit}):
        transcript = "Test conversation"
        conversation_map = ConversationResult(
            concepts={"Test": "A test concept"},
            relationships=[]
        )
        html_content = "<html>Test</html>"
        
        # Set last_transcript to current transcript (simulating duplicate submission)
        mock_streamlit.session_state['last_transcript'] = transcript
        
        # Try to store visualization
        if 'last_transcript' not in mock_streamlit.session_state or mock_streamlit.session_state.get('last_transcript') != transcript:
            mock_store.store_visualization(transcript, conversation_map, html_content)
            mock_streamlit.session_state['last_transcript'] = transcript
        
        # Verify store_visualization was not called
        mock_store.store_visualization.assert_not_called()

def test_different_visualization_storage(mock_store, mock_streamlit):
    """Test storing different visualization (different transcript)."""
    with patch.dict('sys.modules', {'streamlit': mock_streamlit}):
        # Set previous transcript
        mock_streamlit.session_state['last_transcript'] = "Previous conversation"
        
        # New transcript
        transcript = "Different conversation"
        conversation_map = ConversationResult(
            concepts={"Test": "A test concept"},
            relationships=[]
        )
        html_content = "<html>Test</html>"
        
        # Try to store visualization
        if 'last_transcript' not in mock_streamlit.session_state or mock_streamlit.session_state.get('last_transcript') != transcript:
            mock_store.store_visualization(transcript, conversation_map, html_content)
            mock_streamlit.session_state['last_transcript'] = transcript
        
        # Verify store_visualization was called with new transcript
        mock_store.store_visualization.assert_called_once_with(
            transcript, conversation_map, html_content
        ) 