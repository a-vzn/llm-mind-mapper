import pytest
from llm_mind_mapper.mind_mapper import MindMapper
from llm_mind_mapper.conversation_result import ConversationResult

@pytest.fixture
def sample_conversation_map():
    return ConversationResult(
        concepts={
            "test": "A test description",
            "example": "An example description"
        },
        relationships=[("test", "example")]
    )

def test_mind_mapper_initialization(sample_conversation_map):
    mapper = MindMapper(sample_conversation_map)
    assert len(mapper.nodes) == 2
    assert len(mapper.edges) == 1
    assert len(mapper.rejected_edges) == 0

def test_add_valid_edge(sample_conversation_map):
    mapper = MindMapper(sample_conversation_map)
    mapper.add_mm_edge("test", "example")
    assert len(mapper.rejected_edges) == 0

def test_add_invalid_edge(sample_conversation_map):
    mapper = MindMapper(sample_conversation_map)
    mapper.add_mm_edge("test", "nonexistent")
    assert len(mapper.rejected_edges) == 1 