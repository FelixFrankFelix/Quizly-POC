## Main.py

import context as ctx
import boto3
import json
from pinecone import Pinecone

session = boto3.Session()
bedrock = boto3.client(service_name='bedrock-runtime', region_name="us-east-1")
modelId = "anthropic.claude-3-5-sonnet-20240620-v1:0"


prompt_template = """ 
You are a quizbot that provides multiple-choice questions, answers, and explanations to users based on the context provided. The goal is to help users understand the concepts by presenting questions of varying difficulty levels.

Guidelines:

Generate Questions Based on Context: Use the provided context to generate {num_questions} questions related to it.

The context is {context}.
The questions should be relevant to the context and test the user's understanding of the material.

Multiple-Choice Options: Provide 4 options for each question, with one correct answer.

Difficulty Levels:

Level 1 (Very Easy): The question should be straightforward and simple, with easy options. The explanation should be very simplified, focusing on the basic concept.

Level 2 (Easy): The question should be easy but implicit, requiring a bit more thought to answer. The options should also be easy but slightly more nuanced. The explanation should be more complex and go a bit deeper into the concept.

Level 3 (Medium): The question should require some understanding of the topic and be more implicit in nature. The options should provide close alternatives. The explanation should involve practical application or deeper insights into the topic.

Level 4 (Hard): The question should be challenging, requiring a strong understanding of the topic. The options should be distinct but tricky. The explanation should go into detail, possibly covering edge cases or advanced concepts.

Level 5 (Very Hard): The question should be highly complex, possibly involving advanced techniques, theory, or application. The options should be sophisticated and require careful thought. The explanation should dive into advanced concepts, assumptions, and practical considerations.

The difficulty level is {difficulty_level}.

Output Format:
You must use the tool "generate_quiz_questions" to return your response. 
The tool requires a list of questions, where each question is a dictionary containing:
- "question": The question text
- "options": A list of 4 options labeled as strings "A", "B", "C", and "D" (not including the letter labels in the option text)
- "answer": The correct option letter ("A", "B", "C", or "D")
- "explanation": A brief explanation of why the answer is correct

All explanations should be clear and concise, helping the user understand the concept better, not more than a sentence or two.
"""

def get_questions(context_string, difficulty_level=3, num_questions=3):
    """
    Function to get multiple quiz questions based on context.
    
    Parameters:
    - context_string (str): The context to base questions on
    - difficulty_level (int): Level of difficulty from 1-5
    - num_questions (int): Number of questions to generate
    
    Returns:
    - list: A list of question dictionaries
    """
    
    # Define the tool schema for Claude to use
    
    tools = [
        {
            "toolSpec": {
                "name": "generate_quiz_questions",
                "description": "Generate quiz questions based on the context provided.",
                "inputSchema": {
                    "json": {  # This is the key AWS Bedrock expects
                        "type": "object",
                        "properties": {
                            "questions": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "question": {"type": "string"},
                                        "options": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                            "minItems": 4,
                                            "maxItems": 4
                                        },
                                        "answer": {
                                            "type": "string",
                                            "enum": ["A", "B", "C", "D"]
                                        },
                                        "explanation": {"type": "string"}
                                    },
                                    "required": ["question", "options", "answer", "explanation"]
                                }
                            }
                        },
                        "required": ["questions"]
                    }
                }
            }
        }
    ]
            
    # Use Bedrock to generate quiz questions based on the context
    message_list = [{"role": "user", "content": [{"text": f"Generate {num_questions} quiz questions based on the provided context."}]}]
    response = bedrock.converse(
        modelId=modelId,
        messages=message_list,
        system=[
            {"text": prompt_template.format(context=context_string, difficulty_level=difficulty_level, num_questions=num_questions)},
        ],
        toolConfig={
                "tools": tools
            },
        inferenceConfig={
            "maxTokens": 4000,
            "temperature": 0.7
        },
    )
    
    response_message = response['output']['message']

    response_content_blocks = response_message['content']

    content_block = next((block for block in response_content_blocks if 'toolUse' in block), None)

    tool_use_block = content_block['toolUse']

    tool_result_dict = tool_use_block['input']
    
    # Fallback in case tool call fails
    return tool_result_dict

def get_quiz(context, difficulty=3, num_questions=3):
    """Wrapper function to generate and return quiz questions"""
    # Get context
    
    quiz_questions = get_questions(context, difficulty_level=difficulty, num_questions=num_questions)
    return json.dumps({"questions": quiz_questions}, indent=2)


#print(get_quiz())


