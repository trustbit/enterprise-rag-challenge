import os
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import logging
from typing import Optional
import json
import argparse
from datetime import datetime
from .assistant_manager import AssistantManager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv(verbose=True, override=True)

class Answer(BaseModel):
    """Answer information about questions."""

    question: str = Field(
        ...,
        description="The question being asked",
    )
    schema_: str = Field(
        ...,
        alias='schema',
        description="The schema type of the answer",
    )
    answer: Optional[str] = Field(
        ...,
        description="The answer to the question, if schema is 'name' - this should be name of company, if it number it shoulbe be number or N/A",
    )

class Response(BaseModel):
    """Schema converter response"""
    result: str = Field(description="Conversion result")


llm_waek = ChatOpenAI(temperature=0, model="gpt-4o-mini")


def process_questions(input_file: str, output_file: str):
    logger.info(f"Reading questions from {input_file}")
    with open(input_file, 'r') as f:
        questions = json.load(f)

    answers = [Answer(**question_data) for question_data in questions]

    assistant = AssistantManager(
            api_key=os.getenv('OPENAI_API_KEY'),
            assistant_id=os.getenv('OPENAI_ASSISTANT_ID')
        )
    for answer in answers:
        logger.info(f"--------- Invoking the chain with the question: {answer.question}")
        result = assistant.assistant_response(message=answer.question)
        logger.info(f"########### Result: {result}")
        converted_result = assistant.format_response(answer.schema_, result)
        logger.info(f"########### Result Converted: {converted_result.result}")
        logger.info("-------------------------------------------------------------------")
        answer.answer = converted_result.result

    logger.info(f"Saving answers to {output_file}")
    with open(output_file, 'w') as f:
        json.dump([answer.dict(by_alias=True) for answer in answers], f, indent=4)
    logger.info("Answers saved successfully")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process questions and generate answers.")
    parser.add_argument("questions_path", type=str, help="Path to the questions.json file")
    args = parser.parse_args()

    questions_path = args.questions_path
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    answers_path = questions_path.replace("questions.json", f"answers_{timestamp}.json")

    process_questions(questions_path, answers_path)
