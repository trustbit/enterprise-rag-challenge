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


class Answer(BaseModel):
    question_text: Optional[str] = Field(None, description="Text of the question")
    kind: Optional[Literal["number", "name", "boolean", "names"]] = Field(None, description="Kind of the question")
    value: Value = Field(..., description="Answer to the question, according to the question schema")
    references: List[SourceReference] = Field([], description="References to the source material in the PDF file")

    # optional extended data
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


DIR = Path(__file__).parent / "round2"


def load_submissions() -> List[AnswerSubmission]:
    files = (DIR / "submissions").glob("*.json")

    submissions = []
    for f in files:
        v = AnswerSubmission.model_validate_json(f.read_text())
        v.file_name = f.name
        submissions.append(v)

    return submissions


import sqlite3


class ReferenceItem(BaseModel):
    question: str
    pdf_sha1: str
    page_index: int


class AnswerItem(BaseModel):
    question: str
    answer: str

    references: List[ReferenceItem]


Schema = Literal["number", "name", "boolean", "names"]


class Question(BaseModel):
    text: str
    kind: Schema


class QuestionFile(RootModel):
    root: List[Question]


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


class CanonicData(BaseModel):
    kind: Schema
    answers: List[str]
    reference_pools: List[List[str]]


class CanonicFile(RootModel):
    root: Dict[str, CanonicData]


def unwrap(digest) -> List[str]:
    digest, nums = digest.split(":")

    parsed_nums = [int(n) for n in nums.split(",")]

    return [digest + ":" + str(n) for n in parsed_nums]


a1 = CanonicData(
    kind="name",
    answers=["Datalogic"],
    reference_pools=[
        ["980742aa08ea64d552c153bcefbd7e8243fb9efd:72"],  # datalogic
        ["79ffb9b8682aa565172233c070a47d944464644c:137"],
        ["4d3e52b69b4b5366e54ce87cf641b01b1419bdee:84"],  # Incyte
        ["553afbf09b6d83166b17acb02431c6cf38e4defc:48"],
        unwrap("e7a45fed0d7ebfd13a524e7fcc443318bac654e2:71,86,89,101,136")
    ]
)

a2 = CanonicData(
    kind="name",
    answers=["Datalogic"],
    reference_pools=[
        # Datalogic p40 # p43 # p74 # 75,58,79
        unwrap("980742aa08ea64d552c153bcefbd7e8243fb9efd:40,43,74,75,58,79"),
        # Duni Group - 74,137
        unwrap("e7a45fed0d7ebfd13a524e7fcc443318bac654e2:74,137"),
        # NuCana - 167.169.107.181.6.105
        unwrap("9b7fdb871fc4d4a8babc25448257ae0b81a6442d:167,169,107,181,6,105"),
        # Playtech plc - 181,146,147,150
        unwrap("ded965ce7e3ea0ad9b83272b8c36f529793a2887:181,146,147,150"),
        # Atreca	73,83,84,85
        unwrap("5f226fe96206888930e3baaf0bff70d4b0a1db40:73,83,84,85")

    ])

a3 = CanonicData(
    kind="name",
    answers=["Poste Italiane"],
    reference_pools=[
        # Poste Italiane	c741	540
        unwrap("c74139ce26a6f803725f5074a8a0f539abb99c09:540"),
        # NuCana plc	p186
        unwrap("9b7fdb871fc4d4a8babc25448257ae0b81a6442d:186"),
        # Incyte Corporation	4d3e	p84
        unwrap("4d3e52b69b4b5366e54ce87cf641b01b1419bdee:84"),
        # INMUNE BIO INC.	553a	p48
        unwrap("553afbf09b6d83166b17acb02431c6cf38e4defc:48"),
        # Atreca, Inc.	5f22	p82
        unwrap("5f226fe96206888930e3baaf0bff70d4b0a1db40:82")
    ]
)

a57 = CanonicData(
    kind="name",
    answers=["Datalogic"],
    reference_pools=[
        # Atreca, Inc.	5f22	73,83,84,85
        unwrap("5f226fe96206888930e3baaf0bff70d4b0a1db40:73,83,84,85"),
        # INMUNE BIO INC.	553a	49.45.46.50.42
        unwrap("553afbf09b6d83166b17acb02431c6cf38e4defc:49,45,46,50,42"),
        # Datalogic	9807 p40 # p43 # p74 # 75,58,79
        unwrap("980742aa08ea64d552c153bcefbd7e8243fb9efd:40,43,74,75,58,79"),
        # NuCana plc	9b7f	167.169.107.181.6.105
        unwrap("9b7fdb871fc4d4a8babc25448257ae0b81a6442d:167,169,107,181,6,105"),
        # RWE AG	cc0f	3.53.54.119.283
        unwrap("cc0fc5888b99758100a7ff024863fc4337b6b3c5:3,53,54,119,283")
    ]
)

a63 = CanonicData(
    kind="name",
    answers=["Datalogic"],
    reference_pools=[
        # Playtech plc	ded9	170	148	149
        unwrap("ded965ce7e3ea0ad9b83272b8c36f529793a2887:170,148,149"),
        # Datalogic p72 - 98
        unwrap("980742aa08ea64d552c153bcefbd7e8243fb9efd:72"),
        # Duni Group	p71 - Xe7, 86, 89, 101, 136
        unwrap("e7a45fed0d7ebfd13a524e7fcc443318bac654e2:71,86,89,101,136"),
        # Poste Italiane	c741	540
        unwrap("c74139ce26a6f803725f5074a8a0f539abb99c09:540"),
        # Incyte Corporation	4d3e	p84
        unwrap("4d3e52b69b4b5366e54ce87cf641b01b1419bdee:84"),
    ])

a25 = CanonicData(
    kind="name",
    answers=["Datalogic"],
    reference_pools=[
        # Atreca	5f22 - 83	73	84	86
        unwrap("5f226fe96206888930e3baaf0bff70d4b0a1db40:83,73,84,86"),
        # Poste Italiane	c741 - 196	13	20	168	195	440	459	439	542	587	605
        unwrap("c74139ce26a6f803725f5074a8a0f539abb99c09:196,13,20,168,195,440,459,439,542,587,605"),
        # Datalogic	98 - 30	32	33	40	43	44	46	74	110	139	140
        unwrap("980742aa08ea64d552c153bcefbd7e8243fb9efd:30,32,33,40,43,44,46,74,110,139,140"),
        # NuCana plc	9b7f - 167.169.107.181.6.105
        unwrap("9b7fdb871fc4d4a8babc25448257ae0b81a6442d:167,169,107,181,6,105"),
        # RWE AG	cc0f - 200	119	50
        unwrap("cc0fc5888b99758100a7ff024863fc4337b6b3c5:200,119,50")
    ]
)

a84 = CanonicData(
    kind="name",
    answers=["Datalogic"],
    reference_pools=[
        # Incyte Corporation	4d3e	USD		84
        unwrap("4d3e52b69b4b5366e54ce87cf641b01b1419bdee:84"),
        # NMUNE BIO INC.	x55	USD		48
        unwrap("553afbf09b6d83166b17acb02431c6cf38e4defc:48"),
        # Datalogic	EUR	980742aa	845,511,000	72
        unwrap("980742aa08ea64d552c153bcefbd7e8243fb9efd:72"),
        # RWE AG	cc0f	EUR	59245000000	61
        unwrap("cc0fc5888b99758100a7ff024863fc4337b6b3c5:61"),
        # Terns Pharmaceuticals, Inc.	USD	79ffb9b8682aa565172233c070a47d944464644c		137
        unwrap("79ffb9b8682aa565172233c070a47d944464644c:137")
    ]
)

a42 = CanonicData(
    kind="name",
    answers=["Datalogic"],
    reference_pools=[
        # Atreca	5f22	USD	0	83	73	84	86
        unwrap("5f226fe96206888930e3baaf0bff70d4b0a1db40:83,73,84,86"),
        # Poste Italiane	c741	EUR	11900000000	196	13	20	168	195	440	459	439	542	587	605
        unwrap("c74139ce26a6f803725f5074a8a0f539abb99c09:196,13,20,168,195,440,459,439,542,587,605"),
        # Datalogic	98	EUR	654,632,000	30	32	33	40	43	44	46	74	110	139	140
        unwrap("980742aa08ea64d552c153bcefbd7e8243fb9efd:30,32,33,40,43,44,46,74,110,139,140"),
        # Duni GROUP	e7a4	SEK	6,976,000,000	4	8	71	72	85	86	87	101	102	103	150
        unwrap("e7a45fed0d7ebfd13a524e7fcc443318bac654e2:4,8,71,72,85,86,87,101,102,103,150"),
        # Incyte Corporation	4d3e	USD	3,394,635,000	85	97
        unwrap("4d3e52b69b4b5366e54ce87cf641b01b1419bdee:85,97"),
    ]
)

a99 = CanonicData(
    kind="names",
    answers=["Chief Legal Counsel,Chief Financial Officer"],  # Derek McGee
    reference_pools=[
        unwrap("3f36d4f26ada778d89cf5a7344be0b9e9a5223a3:3")
    ]

)

a79 = CanonicData(
    kind="names",
    answers=[
        "Chairman of the Board of Directors,EVP"
    ],

    reference_pools=[
        unwrap("e7a45fed0d7ebfd13a524e7fcc443318bac654e2:78")
    ],
)

CUSTOM_ANSWERS = {
    """Which of the companies had the lowest total assets in EUR at the end of the period listed in annual report: "Datalogic", "Terns Pharmaceuticals, Inc.", "Incyte Corporation", "INMUNE BIO INC.", "Duni Group"? If data for the company is not available, exclude it from the comparison. If only one company is left, return this company.""":
        a1,
    """Which of the companies had the lowest net income in EUR at the end of the period listed in annual report: "Datalogic", "NuCana plc", "Duni Group", "Playtech plc", "Atreca, Inc."? If data for the company is not available, exclude it from the comparison. If only one company is left, return this company.""": a2,
    """Which of the companies had the lowest total assets in EUR at the end of the period listed in annual report: "Poste Italiane", "NuCana plc", "Incyte Corporation", "INMUNE BIO INC.", "Atreca, Inc."? If data for the company is not available, exclude it from the comparison. If only one company is left, return this company.""": a3,
    """Which of the companies had the lowest net income in EUR at the end of the period listed in annual report: "Atreca, Inc.", "INMUNE BIO INC.", "Datalogic", "NuCana plc", "RWE AG"? If data for the company is not available, exclude it from the comparison. If only one company is left, return this company.""": a57,
    # 63
    """Which of the companies had the lowest total assets in EUR at the end of the period listed in annual report: "Playtech plc", "Datalogic", "Duni Group", "Poste Italiane", "Incyte Corporation"? If data for the company is not available, exclude it from the comparison. If only one company is left, return this company.""": a63,
    # 25
    """Which of the companies had the lowest total revenue in EUR at the end of the period listed in annual report: "Atreca, Inc.", "Poste Italiane", "Datalogic", "NuCana plc", "RWE AG"? If data for the company is not available, exclude it from the comparison. If only one company is left, return this company.""": a25,
    # 84
    """Which of the companies had the lowest total assets in EUR at the end of the period listed in annual report: "Incyte Corporation", "INMUNE BIO INC.", "Datalogic", "Terns Pharmaceuticals, Inc.", "RWE AG"? If data for the company is not available, exclude it from the comparison. If only one company is left, return this company.""": a84,
    # 42
    """Which of the companies had the lowest total revenue in EUR at the end of the period listed in annual report: "Atreca, Inc.", "Poste Italiane", "Datalogic", "Duni Group", "Incyte Corporation"? If data for the company is not available, exclude it from the comparison. If only one company is left, return this company.""": a42,
    # 99
    """Which leadership positions changed at Origin Bancorp, Inc. in the reporting period? If data is not available, return 'N/A'. Give me the title of the position.""": a99,
    # 79
    """Which leadership positions changed at Duni Group in the reporting period? If data is not available, return 'N/A'. Give me the title of the position.""": a79,

}

DISQUALIFY = [
    # because hard to tell what is product
    "What are the names of new products launched by Albany International Corp. as mentioned in the annual report?",

]


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


def load_canonic_answers():
    file = DIR / "answers.json"

    # reload
    data = CanonicFile.model_validate_json(file.read_text())
    schemas = data.root

    print(file.absolute())

    console = Console()

    rankings = []

    for submission in load_submissions():
        # rank submission
        val_score = 0

        index = {a.question_text: a for a in submission.answers}
        stats = defaultdict(int)
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

            ref_score = 0

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
    table.add_column("Rank")
    table.add_column("Email")
    table.add_column("Team")
    table.add_column("Signature")
    table.add_column("R score")
    table.add_column("G score")
    table.add_column("Score")
    table.add_column("Missing")
    table.add_column("Missing Ref")
    table.add_column("No rank")
    table.add_column("Val Accuracy")

    df_records = []

    for i, r in enumerate(rankings):
        team = r.submission.submission_name
        signature = r.submission.signature[:8]

        accuracy = 0

        accuracy = 100.0 * r.val_score / (100 - r.no_rank)

        table.add_row(
            str(i + 1),
            r.submission.team_email,
            team.replace("\n", " "),
            signature,
            f"{r.ref_score:.1f}",
            f"{r.val_score:.1f}",
            f"{r.score:.1f}",
            str(r.missing),
            str(r.missing_ref),
            str(r.no_rank),
            f"{accuracy:.2f} %"
        )

        df_records.append({
            "rank": i + 1,
            "email": r.submission.team_email,
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

    # print
    console.print(table)

    df = pd.DataFrame(df_records)
    df.to_csv(DIR / "ranking.csv", index=False)

    # read all references!


if __name__ == "__main__":
    load_canonic_answers()


def test():
    load_canonic_answers()
    answers = load_submissions()
    assert len(answers) > 0

    print(answers[0].team_email)
