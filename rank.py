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


def grade_answer(true_answer, true_references, answer, schema) -> float:
    # answer is correct if it is in the list of expected answers
    value = answer["value"]
    # TODO include scoring of references
    references = answer["references"]

    is_na_expected = true_answer in VALID_NONES
    is_na_actual = value in VALID_NONES

    if is_na_expected:
        return 1 if is_na_actual else 0

    # so NA is not expected. But what if we have NA in the actual answer?
    if is_na_actual:
        return 0

    if schema == "number":
        expected_value = float(true_answer)
        try:
            actual_value = float(value)
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
        expected_value = bool(true_answer)
        actual_value = value in ["True", "true", "1", "yes", True]
        return 1 if actual_value == expected_value else 0

    elif schema == "name":
        actual_value = str(value).strip().lower()
        expected_value = str(true_answer).strip().lower()
        return 1 if actual_value == expected_value else 0

    elif schema == "names":
        # TODO maybe introduce fuzzy logic here, as e.g. roles like "Senior Independent Non-Executive Director" might be prone to slight mistakes?
        # TODO maybe similarly for "name" above
        actual_values = [str(v).strip().lower() for v in value]
        expected_values = [str(v).strip().lower() for v in true_answer]
        # TODO check logic below
        return len(set(actual_values) & set(expected_values)) / len(set(actual_values) | set(expected_values))

    else:
        raise Exception(f"Unknown schema {schema}")


@dataclass
class TeamRank:
    submission_name: str
    team_email: str
    score: int
    answers: List[str]


def rank_team(expected, submission) -> TeamRank:
    score = 0
    ideal_score = 0
    for expected, answer in zip(expected, submission["answers"]):
        true_answers = expected["ground_truth"]
        if type(true_answers) is not list:
            true_answers = [true_answers]
        true_references = expected["references"]
        schema = expected["kind"]

        category, max_score = get_answer_category(true_answers)
        # TODO but if NA is valid, and the team answers a non-NA value, shouldn't it get more points?
        #  (now they get 1 point for both answers, NA and actual retrieved value)
        ideal_score += max_score

        if answer is None:
            # no answer
            # TODO can this even happen?
            continue

        # if multiple answers are valid, take the best grade
        answer_grade = max(grade_answer(true_answer, true_references, answer, schema) for true_answer in true_answers)
        score += answer_grade * max_score

    print(f"{submission['submission_name']} score: {score} / {ideal_score}")
    # normalize score
    score = 100.0 * score / ideal_score
    if score < 0:
        score = 0

    # TODO do we really want to make the score int? Why not keep (rounded) floats?
    return TeamRank(submission["submission_name"], submission["team_email"], int(score), submission["answers"])


@click.command()
@click.argument("folder", type=click.Path(exists=True))
def run(folder: str):
    expected_file = Path(folder) / "answers.json"

    with expected_file.open("r") as file:
        expected = json.load(file)

    files = Path(folder).glob("submissions/*.json")

    # TODO filter out submissions with identical submission_name and team_email and only keep latest

    records = []
    team_answers = []
    for f in sorted(files):
        try:
            with f.open("r") as file:
                submission = json.load(file)

            team_rank = rank_team(expected, submission)

            records.append(
                {
                    "id": submission["submission_name"] + "-" + submission["team_email"],
                    "score": team_rank.score,
                    "json_name": f.stem
                }
            )
            values_only = [x["value"] for x in submission["answers"]]
            team_answers.append(values_only)

        except Exception as e:
            # ansi color red
            raise e

    true_answers = [x['ground_truth'] for x in expected]
    team_ids = ["ground_truth"] + [x["id"] for x in records]
    answers = [true_answers] + team_answers
    answers_df = pd.DataFrame(answers).T
    answers_df.columns = team_ids
    answers_df.to_csv(Path(folder) / "answers.csv", index=False)

    teams_metadata = pd.read_csv(Path(folder) / "teams.csv", index_col=False)
    teams_metadata["id"] = teams_metadata["submission_name"] + "-" + teams_metadata["team_email"]

    teams_scores_df = teams_metadata.merge(pd.DataFrame(records), on="id", how="left")

    # only keep relevant columns
    df_rec = teams_scores_df[["submission_name", "team_email", "score", "json_name", "more"]]  # TODO update to more metadata

    # sort by score
    df_rec = df_rec.sort_values("score", ascending=False)

    # print as table to console, no index
    print(df_rec.to_string(index=False))
    # save to scores.csv
    df_rec.to_csv(Path(folder) / "scores.csv", index=False)


if __name__ == "__main__":
    run()
