import json
from dataclasses import dataclass
from pathlib import Path
from typing import List
import csv
import click

import pandas as pd


VALID_NONES = ["N/A", "n/a"]






def is_answer_correct(question, actual_answer, schema, expected_answers):

    scores = []








    try:

        for expected,score in expected_answers:
            if expected in VALID_NONES:
                passed = actual_answer in VALID_NONES
                scores.append(score if passed else 0)
            elif actual_answer in VALID_NONES:
                scores.append(0)
            elif schema == "number":
                try:
                    actual_value = float(actual_answer)
                    expected_value = float(expected)

                    if actual_value == expected_value:
                        scores.append(score)
                    # give half score if the difference is less than 10%
                    elif abs(actual_value - expected_value) < 0.1 * expected_value:
                        scores.append(score / 2)
                    else:
                        scores.append(0)

                except ValueError:
                    scores.append(0)
            elif schema == "boolean":
                try:
                    passed = bool(actual_answer) == bool(expected)
                except ValueError:
                    passed = False
                scores.append(score if passed else 0)
            elif schema == "name":
                passed = str(actual_answer) == str(expected)
                scores.append(score if passed else 0)
            else:

                raise Exception(f"Unknown schema {schema}")


    except Exception as e:
        raise Exception(f"Error processing {question}: {e}") from e

    if len(scores) == 0:
        return 0

    return max(scores)


@dataclass
class TeamRank:
    name: str
    score: int
    answers: List[str]

def rank_team(expected, file) -> TeamRank:
    team = file.stem

    with file.open("r") as file:
        submission = json.load(file)

    if team == "anonymous1652":
        # this team returned a list of answers instead of a dict
        answer_list = submission['answer']
        question_list = submission['question'].values()
    else:

        answer_list = [a["answer"] for a in submission]
        question_list = [a["question"] for a in submission]

    score = 0

    for answer, question, ex in zip(answer_list, question_list, expected):

        # check if the question is the same. Use only first 20 letters, as some teams
        # didn't handle unicode symbols correctly
        if question[:20] != ex["question"][:20]:
            # use red ANSI color
            raise Exception(f"Question mismatch: {question} != {ex['question']}")

        score += is_answer_correct(ex["question"], answer, ex["schema"], ex["answer"])
    return TeamRank(team, score, answer_list)


@click.command()
@click.argument("folder", type=click.Path(exists=True))
def run(folder: str):

    expected_file = Path(folder) / "answers.json"

    with expected_file.open("r") as file:
        expected = json.load(file)


    # create all N/A team
    # copy expected



    files = Path(folder).glob("answers/*.json")


    answers = [{'real':x['answer']} for x in expected]


    for f in sorted(files):

        team_name = f.stem
        try:
            team = rank_team(expected, f)

            for a,t in zip(answers, team.answers):
                a[team_name] = t

            print(f"{team_name}: {team.score}")

        except Exception as e:
            # ansi color red
            print(f"{team_name}: \033[91m{e}\033[0m")

    df = pd.DataFrame(answers)
    df.to_csv(Path(folder) / "answers.csv", index=False)


if __name__ == "__main__":
    run()