INITIALIZE_MAP_PROMPT_TEMPLATE = """
You are a conversation analyzer that extracts concepts and their relationships from conversations.

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

Provide only the JSON output, no additional text or explanations.
"""

INCLUDE_REJECTED_EDGES_PROMPT_TEMPLATE = """
You are a conversation analyzer that given the following:
 - An original chat transcript: {conversation}
 - A mind map in in the form of a JSON object with a dictionary: {mind_map}
 - A list of concepts that were rejected during the initial analysis that need to be defined given the conversation: {rejected_concepts}
 - A list of relationships that were rejected during the initial analysis that need to be included in the updated mindmap: {rejected_edges}

Task: Update the mind map with the rejected concepts and relationships based on the conversation.

Guidelines:
1. Each concept should be a key topic or entity from the conversation
2. Each concept's description should explain its role or context in the conversation
3. Relationships should connect related concepts using their exact names
4. Only include relationships between concepts that are explicitly mentioned
5. Make sure all concepts in relationships exist in the concepts dictionary
6. Make sure the returned structure is a combination of the originally provided mind map and the newly defined concepts and relationships

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

Provide only the JSON output, no additional text or explanations.
"""