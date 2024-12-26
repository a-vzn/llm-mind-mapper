from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM
from langchain.output_parsers import PydanticOutputParser
import json

from .conversation_result import ConversationResult

class ConversationMapperLLMClient:
    def __init__(self, conversation, llm):
        self.conversation = conversation
        self.llm = llm
        self.parser = PydanticOutputParser(pydantic_object=ConversationResult)
        self.prompt_template = PromptTemplate(
            input_variables=["conversation"],
            template="""You are a conversation analyzer that extracts concepts and their relationships from conversations.

Task: Analyze the conversation below and create a structured representation of the concepts discussed and their relationships.

Required Output Format:
{{
    "concepts": {{
        "concept1": "description1",
        "concept2": "description2",
        ...
    }},
    "relationships": [
        ["concept1", "concept2"],
        ["concept2", "concept3"],
        ...
    ]
}}

Guidelines:
1. Each concept should be a key topic or entity from the conversation
2. Each concept's description should explain its role or context in the conversation
3. Relationships should connect related concepts using their exact names
4. Only include relationships between concepts that are explicitly mentioned
5. Make sure all concepts in relationships exist in the concepts dictionary

Example Output:
{{
    "concepts": {{
        "Mobile App Development": "The main project being discussed involving app creation",
        "User Authentication": "Security feature for user verification and access control"
    }},
    "relationships": [
        ["Mobile App Development", "User Authentication"]
    ]
}}

Now analyze this conversation:
{conversation}

Provide only the JSON output, no additional text or explanations."""
        )

    def map_conversation(self):
        try:
            # Get LLM response
            response = self.llm.invoke(
                self.prompt_template.format(conversation=self.conversation)
            )
            
            # Parse JSON response
            json_response = json.loads(response)
            
            # Convert to ConversationResult
            result = ConversationResult(
                concepts=json_response["concepts"],
                relationships=json_response["relationships"]
            )
            
            return result
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error processing conversation: {str(e)}")