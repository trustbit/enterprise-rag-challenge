import importlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import List
import click

import pandas as pd


VALID_NONES = ["N/A", "n/a"]



def get_answer_category(expected_answers: list) -> (str, float):

    # if N/A is a valid answer, return, then it can be guessed, score it lower
    if any(a in VALID_NONES for a in expected_answers):
        return "N/A", 1

    return "retrieval", 2


def grade_answer(actual_answer, schema, expected_answer) -> float:

    # answer is correct if it is in the list of expected answers



    is_na_expected = expected_answer in VALID_NONES
    is_na_actual = actual_answer in VALID_NONES

    if is_na_expected:
        return 1 if is_na_actual else 0

    # so NA is not expected. But what if we have NA in the actual answer?
    if is_na_actual:
        return 0


    if schema == "number":
        expected_value = float(expected_answer)
        try:
            actual_value = float(actual_answer)
        except ValueError:
            # invalid format
            return 0

        # if answer is within 1 % of the expected value, give full score
        if abs(actual_value - expected_value) < 0.01 * expected_value:
            return 1

        # if answer is within 10 % of the expected value, give half score
        if abs(actual_value - expected_value) < 0.1 * expected_value:
            return 0.5

        return 0

    elif schema == "boolean":
        expected_value = bool(expected_answer)
        actual_value = actual_answer in ["True", "true", "1", "yes", True]
        return 1 if actual_value == expected_value else 0

    elif schema == "name":
        actual_value = str(actual_answer).strip().lower()
        expected_value = str(expected_answer).strip().lower()
        return 1 if actual_value == expected_value else 0
    else:
        raise Exception(f"Unknown schema {schema}")

@dataclass
class TeamRank:
    name: str
    score: int
    answers: List[str]

def rank_team(expected, file) -> TeamRank:
    team = file.stem



    with file.open("r") as file:
        submission = json.load(file)


    if team == "anonymous_1652":
        # this team returned a list of answers instead of a dict
        answer_list = submission['answer'].values()
        question_list = submission['question'].values()
    else:
        answer_list = [a["answer"] for a in submission]
        question_list = [a["question"] for a in submission]

    score = 0
    ideal_score = 0
    for answer, question, ex in zip(answer_list, question_list, expected):

        # check if the question is the same. Use only first 20 letters, as some teams
        # didn't handle unicode symbols correctly
        if question[:20] != ex["question"][:20]:
            # use red ANSI color
            raise Exception(f"Question mismatch: {question} != {ex['question']}")

        valid_answers = ex["answer"]
        schema = ex["schema"]


        category, max_score = get_answer_category(valid_answers)
        ideal_score += max_score


        if answer is None:
            # no answer
            continue

        # if multiple answers are valid, take the best grade
        answer_grade = max(grade_answer(answer, schema, a) for a in valid_answers)
        score += answer_grade * max_score


    print(f"Score: {score} / {ideal_score}")
    # normalize score
    score = 100.0 * score / ideal_score
    if score < 0:
        score = 0

    return TeamRank(team, int(score), answer_list)

import importlib.util

@click.command()
@click.argument("folder", type=click.Path(exists=True))
def run(folder: str):

    expected_file = Path(folder) / "answers.json"

    with expected_file.open("r") as file:
        expected = json.load(file)

    # dynamically load file FOLDER/teams.py
    # and get value of TEAMS variable (it is a list)
    teams_file = Path(folder) / "teams.py"
    spec = importlib.util.spec_from_file_location("teams", teams_file)
    teams_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(teams_module)
    teams = {t.file_name: t.__dict__ for t in teams_module.TEAMS}










    files = Path(folder).glob("answers/*.json")


    answers = [{'real':x['answer']} for x in expected]

    records = []


    for f in sorted(files):

        team_name = f.stem.replace("_", " ")

        team_obj = teams[f.stem]


        try:
            team = rank_team(expected, f)

            for a,t in zip(answers, team.answers):
                a[team_name] = t

            print(f"{team_name}: {team.score}")

            learned_from_ai_research = team_obj['learned_from_ai_research']
            affiliated = "TimeToAct" in team_obj['affiliation']

            records.append({
                'Team': team_obj['team_name'],
                'Score': team.score,
                'Model': team_obj['model_name'],
                'Local': "⭐" if team_obj['is_local_model'] else "",
                'Design': team_obj['architecture_short'] or "",
                'Cost': team_obj['total_prefill_and_answer_costs'] or "",
                'Source': team_obj['source_code'] or "",
                'AIR': "Yes" if learned_from_ai_research else "",
                'TTA': "Yes" if affiliated else "",
            })

        except Exception as e:
            # ansi color red
            raise e


    df = pd.DataFrame(answers)
    df.to_csv(Path(folder) / "answers.csv", index=False)


    df_rec = pd.DataFrame(records)
    # sort by score
    df_rec = df_rec.sort_values(by='Score', ascending=False)

    # print as table to console, no index
    print(df_rec.to_string(index=False))
    # save to scores.csv
    df_rec.to_csv(Path(folder) / "scores.csv", index=False)

if __name__ == "__main__":
    run()