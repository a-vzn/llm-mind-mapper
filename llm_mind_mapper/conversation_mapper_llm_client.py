from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM
from langchain.output_parsers import PydanticOutputParser
import json

from mind_mapper import MindMapper

from .conversation_result import ConversationResult
from .prompt_templates import INITIALIZE_MAP_PROMPT_TEMPLATE, INCLUDE_REJECTED_EDGES_PROMPT_TEMPLATE

class ConversationMapperLLMClient:
    def __init__(self, conversation, llm):
        self.conversation = conversation
        self.llm = llm
        self.parser = PydanticOutputParser(pydantic_object=ConversationResult)
        self.initialize_map_prompt_template = INITIALIZE_MAP_PROMPT_TEMPLATE
        self.incorporate_rejected_edges_prompt_template = INCLUDE_REJECTED_EDGES_PROMPT_TEMPLATE
        self.mind_mapper = None

    def map_conversation(self):
        try:
            # Get LLM response
            response = self.llm.invoke(
                self.initialize_map_prompt_template.format(conversation=self.conversation)
            )
            
            # Parse JSON response
            json_response = json.loads(response)
            
            # Convert to ConversationResult
            self.mind_mapper = MindMapper(
                ConversationResult(
                    **json_response
                )
            )

            
            response = self.llm.invoke(
                self.incorporate_rejected_edges_prompt_template.format(
                    conversation=self.conversation,
                    mind_map=self.mind_mapper.to_json(),
                    rejected_concepts=self.mind_mapper.missing_concepts,
                    rejected_edges=self.mind_mapper.rejected_edges
                )
            )

            self.mind_mapper = MindMapper(
                ConversationResult(
                    **json.loads(response)
                )
            )

            return self.mind_mapper
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error processing conversation: {str(e)}")
        
if __name__ == "__main__":
    llm = OllamaLLM(model="llama3.1")
    client = ConversationMapperLLMClient(
        conversation="""
Alex: Hey Jamie, what do you usually do in your free time? I feel like I never have hobbies anymore.

Jamie: It depends on my mood, but I love reading mystery novels and baking. They help me relax and feel productive at the same time. What about you?

Alex: Honestly, I’ve been stuck in a rut. I used to enjoy painting, but I haven’t done it in months. I feel like I need something new to try.

Jamie: Why not get back into painting? Sometimes all it takes is setting aside a bit of time and making it a priority.

Alex: Maybe. I just feel like I’m out of practice. I’ve also been thinking about trying gardening. I’ve heard it’s really therapeutic.

Jamie: Gardening sounds great! Plus, you can grow your own vegetables or flowers, which is super rewarding. I started with a small herb garden, and it’s been fun.

Alex: That’s a good idea. What herbs do you recommend starting with?

Jamie: Basil, mint, and parsley are great for beginners. They grow quickly, and you can use them in cooking, which feels so satisfying.

Alex: That does sound rewarding. I think I’ll give it a shot. Thanks for the advice!

Jamie: Anytime! Let me know how it goes. Maybe we can swap gardening tips soon.""",
        llm=llm
    )
    client.map_conversation()