import json

def calculate_correct_answers(source_file: str, result_file: str) -> int:
    """
    Calculate the number of correct answers by comparing the result file with the source of truth file.

    Args:
        source_file (str): Path to the source of truth JSON file.
        result_file (str): Path to the result JSON file.

    Returns:
        int: The number of correct answers.
    """
    with open(source_file, 'r') as f:
        source_data = json.load(f)

    with open(result_file, 'r') as f:
        result_data = json.load(f)

    correct_count = 0

    for source, result in zip(source_data, result_data):
        if source['answer'] == result['answer']:
            correct_count += 1

    return correct_count
