from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM
from langchain.output_parsers import PydanticOutputParser

from conversation_result import ConversationResult

class ConversationMapperLLMClient:
    def __init__(self, conversation, llm):
        self.conversation = conversation
        self.llm = llm
        self.parser = PydanticOutputParser(pydantic_object=ConversationResult)
        self.prompt_template = PromptTemplate(
            template="""
            1. Extract key-value pairs where each key represents a concept, and each value is a description or context about that concept.
                These descriptions should come largely from the conversation, not from any prior context you as the model may have on these topics, 
                but you may include some additional information if you deem it necessary.
            2. Identify relationships between these concepts and represent them as key-to-key tuples.

            Analyze the converation and provide the concepts and relationships in the following format:
            {parser_instructions}

            Strictly adhere to the above format, this should be the only output.
            There is no need for additional information or a script to extract the info.
            STRICTLY stick to the format provided above, nothing more or less.
            There should be no additional layer of nesting, for concepts the keys at the top level are the names of the concepts, and the values of those keys are dictionaries. NOTHING ELSE no extra nesting. NONE AT ALL. You will die if you do.

            Err on the side of more concepts and more relationships between concepts rather than fewer.
            But ensure that the conversation supports a tangible connection before asserting a relationship between two concepts.
            Strictly do not hallucinate connections.
            ANY ENTRIES IN THE RELATIONSHIPS OBJECT MUST HAVE ENTRIES IN THE CONCEPTS OBJECT.

            Conversation:
            {conversation}
            """
        )
        self.chain = self.prompt_template | self.llm | self.parser

    def map_conversation(self):
        response = self.chain.invoke(
            input={
                "conversation": self.conversation,
                "parser_instructions": self.parser.get_format_instructions()
            }
        )
        return response