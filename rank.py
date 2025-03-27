from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Literal, List, Union, Dict
import pandas as pd
from pydantic import BaseModel, Field, RootModel

from rich.table import Table
from rich.console import Console


class SourceReference(BaseModel):
    pdf_sha1: str = Field(..., description="SHA1 hash of the PDF file")
    page_index: int = Field(..., description="Zero-based physical page number in the PDF file")


Value = Union[float, str, bool, List[str], Literal["N/A"]]
Schema = Literal["number", "name", "boolean", "names"]


class Answer(BaseModel):
    question_text: Optional[str]
    kind: Optional[Schema]
    value: Value
    references: List[SourceReference] = []

    # extended gt data
    gt_value: Optional[List[Value]] = None
    gt_refs: List[List[str]] = None
    debug: List[str] = None


class AnswerSubmission(BaseModel):
    answers: List[Answer] = Field(..., description="List of answers to the questions")
    team_email: str = Field(..., description="Email that your team used to register for the challenge")
    submission_name: str = Field(..., description="Unique name of the submission (e.g. experiment name)")
    signature: str
    file_name: str = ""
    time: str = ""


class CanonicData(BaseModel):
    kind: Schema
    answers: List[str]
    reference_pools: List[List[str]]


class CanonicFile(RootModel):
    root: Dict[str, CanonicData]


@dataclass
class Ranking:
    submission: AnswerSubmission
    missing: int = 0
    missing_ref: int = 0
    no_rank: int = 0
    score: float = 0
    val_score: float = 0
    ref_score: float = 0
    elapsed_hours: float = 0


DIR = Path(__file__).parent / "round2"


def load_submissions() -> List[AnswerSubmission]:
    files = (DIR / "submissions").glob("*.json")
    submissions = []
    for f in files:
        v = AnswerSubmission.model_validate_json(f.read_text())
        v.file_name = f.name
        submissions.append(v)
    return submissions


def compare(schema: Schema, actual: str, predicted: Value) -> float:
    if predicted == "N/A" and actual == "N/A":
        return 1.0

    if actual == "N/A" or predicted == "N/A":
        return 0.0

    if schema == "number":
        try:
            actual = float(actual)
            predicted = float(predicted)
        except ValueError:
            return 0.0

        # if answer is within 1 % of the expected value, give full score
        if abs(predicted - actual) < 0.01 * actual:
            return 1.0

        return 0.0

    elif schema == "boolean":
        if str(actual).lower() == str(predicted).lower():
            return 1.0
        else:
            return 0.0

    elif schema == "name":
        if str(actual).strip().lower() == str(predicted).strip().lower():
            return 1.0
        else:
            return 0.0

    elif schema == "names":
        # ensure that predicted is list of strings
        if isinstance(predicted, str):
            # convert to list of strings by splitting
            predicted = predicted.split(",")
            # and trip spaces
            predicted = [p.strip() for p in predicted]

        actual_names = str(actual).strip().lower().split(",")
        predicted_names = [str(p).strip().lower() for p in predicted]

        # jaqqard distance
        intersection = len(set(actual_names).intersection(predicted_names))
        union = len(set(actual_names).union(predicted_names))
        return 1.0 * intersection / union

    else:
        raise Exception(f"Unknown schema {schema}")


def load_canonic_answers():
    file = DIR / "answers.json"
    data = CanonicFile.model_validate_json(file.read_text())
    schemas = data.root

    console = Console(width=120)
    rankings = []

    for submission in load_submissions():
        stats = defaultdict(int)
        index = {a.question_text: a for a in submission.answers}

        for q, data in schemas.items():
            predicted = index.get(q)
            if predicted is None:
                stats["missing"] += 1
                continue

            if not data.answers:
                stats["no_rank"] += 1
                continue

            predicted.gt_value = data.answers
            predicted.gt_refs = data.reference_pools
            predicted.debug = []

            # if we have multiple answers possible, pick the highest score
            val_score = max([compare(data.kind, a, predicted.value) for a in data.answers])

            # convert answer refs to hash:page format
            predicted_refs = [r.pdf_sha1 + ":" + str(r.page_index) for r in predicted.references]

            max_ref_score = 1.0

            if len(data.reference_pools) == 0 and len(predicted_refs) == 0:
                pass
            else:
                # flatten all pools to one array
                expected_refs = []
                for expected in data.reference_pools:
                    expected_refs.extend(expected)

                max_ref_score = 1.0

                for p in predicted_refs:
                    if p not in expected_refs:
                        max_ref_score -= 0.1

                for proof_neded in data.reference_pools:
                    found_proof = len(set(predicted_refs).intersection(proof_neded)) > 0
                    if not found_proof:
                        max_ref_score -= 0.25

            stats["val_score"] += val_score

            ref_score = max(0.0, max_ref_score)
            predicted.debug.append(f"Ref_score: {ref_score:.2f}")

            stats["ref_score"] += ref_score

            predicted.debug.append(f"Score: {val_score}")

        val_score = stats["val_score"]
        ref_score = stats["ref_score"]

        score = (val_score + ref_score / 2.0)

        time = datetime.strptime(submission.time, "%Y-%m-%d, %H:%M:%S")

        # started =  — 27/02/2025, 13:29
        started = datetime.strptime("2025-02-27, 12:30", "%Y-%m-%d, %H:%M")
        elapsed_hours = (time - started).total_seconds() / 3600.0

        rankings.append(Ranking(
            submission=submission,
            missing=stats["missing"],
            missing_ref=stats["missing_refs"],
            no_rank=stats["no_rank"],
            score=score,
            ref_score=ref_score,
            val_score=val_score,
            elapsed_hours=elapsed_hours
        ))

        # save submission to "ranked" folder
        ranked_dir = DIR / "ranked"

        # OPTIONAL: save ranked submissions
        # ranked_dir.mkdir(exist_ok=True)
        # ranked_dir.joinpath(submission.file_name).write_text(
        #     submission.model_dump_json(indent=2), encoding="utf-8"
        # )

    # sort by score descending
    rankings.sort(key=lambda x: x.score, reverse=True)

    # rankings.sort(key=lambda x: x.submission.time)

    # now render to table
    table = Table(title="Ranking", row_styles=["dim", ""])

    table.add_column("Rank", width=20)
    table.add_column("Submission", width=40)
    table.add_column("R", width=20)
    table.add_column("G", width=20)
    table.add_column("Score", width=20)

    df_records = []

    for i, r in enumerate(rankings):
        team = r.submission.submission_name
        signature = r.submission.signature[:8]

        accuracy = 100.0 * r.val_score / (100 - r.no_rank)

        table.add_row(
            str(i + 1),
            # r.submission.team_email,
            team.replace("\n", " "),
            f"{r.ref_score:.1f}",
            f"{r.val_score:.1f}",
            f"{r.score:.1f}",
        )

        df_records.append({
            "rank": i + 1,
            "team": team.replace("\n", " "),
            "signature": signature,
            "R": f"{r.ref_score:.1f}",
            "G": f"{r.val_score:.1f}",
            "Score": f"{r.score:.1f}",
            "Missing": str(r.missing),
            "Missing Ref": str(r.missing_ref),
            "No rank": str(r.no_rank),
            "Val Accuracy": f"{accuracy:.2f} %",
            "Elapsed": f"{r.elapsed_hours:.2f}"
        })

    console.print(table)
    df = pd.DataFrame(df_records)
    df.to_csv(DIR / "ranking.csv", index=False)


if __name__ == "__main__":
    load_canonic_answers()
