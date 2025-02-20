"""
This is a prototype of deterministic question generator to test RAG systems.

STEP1: Given a seed number, it will generate a subset of files to include in the test. This subset will
include SHA1 hashes of the files to ensure that the same files are used in the test. It will also include
the company name extracted from that PDF.

STEP2: Given the subset of files, it will generate a set of questions to ask about the companies
"""
import json
from pathlib import Path
from random import randint
import click
import pandas as pd

from typing import Literal, Dict, List, Optional, Union

from pydantic import BaseModel, RootModel, Field

industries = [
    "Technology", "Financial Services", "Healthcare", "Automotive",
    "Retail", "Energy and Utilities", "Hospitality", "Telecommunications",
    "Media & Entertainment", "Pharmaceuticals", "Aerospace & Defense",
    "Transport & Logistics", "Food & Beverage"
]


class EndOfPeriod(BaseModel):
    year: int
    month: int


class AnnualReportInfo(BaseModel):
    end_of_period: EndOfPeriod
    company_name: str
    major_industry: Literal[tuple(industries)]
    mentions_recent_mergers_and_acquisitions: bool
    has_leadership_changes: bool
    has_layoffs: bool
    has_executive_compensation: bool
    has_rnd_investment_numbers: bool
    has_new_product_launches: bool
    has_capital_expenditures: bool
    has_financial_performance_indicators: bool
    has_dividend_policy_changes: bool
    has_share_buyback_plans: bool
    has_capital_structure_changes: bool
    mentions_new_risk_factors: bool
    has_guidance_updates: bool
    has_regulatory_or_litigation_issues: bool
    has_strategic_restructuring: bool
    has_supply_chain_disruptions: bool
    has_esg_initiatives: bool


class ReportEntry(BaseModel):
    letters: int
    pages: int
    meta: AnnualReportInfo
    currency: Dict[str, int]
    sha1: str

    def main_currency(self) -> Optional[str]:
        if not self.currency:
            return None
        return max(self.currency, key=self.currency.get)


ReportFile = Dict[str, ReportEntry]


class Question(BaseModel):
    text: str
    kind: Literal["number", "name", "boolean", "names"]


class SourceReference(BaseModel):
    pdf_sha1: str = Field(..., description="SHA1 hash of the PDF file")
    page_index: int = Field(..., description="Zero-based physical page number in the PDF file")


class Answer(BaseModel):
    question_text: Optional[str] = Field(None, description="Text of the question")
    kind: Optional[Literal["number", "name", "boolean", "names"]] = Field(None, description="Kind of the question")
    value: Union[float, str, bool, List[str], Literal["N/A"]] = Field(..., description="Answer to the question, according to the question schema")
    references: List[SourceReference] = Field([], description="References to the source material in the PDF file")


class AnswerSubmission(BaseModel):
    answers: List[Answer] = Field(..., description="List of answers to the questions")
    team_email: str = Field(..., description="Email that your team used to register for the challenge")
    submission_name: str = Field(..., description="Unique name of the submission (e.g. experiment name)")


class SubsetFile(RootModel):
    root: List[ReportEntry]


class DeterministicRNG:
    def __init__(self, seed: int):
        if seed == 0:
            seed = randint(1, 2 ** 32)
        self.state = seed

    def random(self, n: int) -> int:
        # LCG parameters
        a, c, m = 1664525, 1013904223, 2 ** 32

        # Update state
        self.state = (a * self.state + c) % m

        # Return a number between 0 and n
        return self.state % n

    def choice(self, seq: List) -> str:
        if len(seq) == 0:
            raise ValueError("Cannot choose from an empty sequence")
        return seq[self.random(len(seq))]

    def sample(self, seq: List, k: int) -> List:
        pool = list(seq)
        results = []
        for i in range(k):
            j = self.random(len(pool))
            results.append(pool[j])
            pool[j] = pool[-1]
            pool.pop()
        return results

        # pick k unique elements from seq


@click.group()
def cli():
    pass


def load_dataset() -> dict[str, ReportEntry]:
    dataset = Path(__file__).parent / "dataset_v2.json"

    obj = json.loads(dataset.read_text())

    result = {}

    for k, v in obj.items():
        if "sha1" not in v:
            continue
        if "meta" not in v:
            continue
        result[k] = ReportEntry.model_validate(v)

    return result


@cli.command()
@click.option("--count", default=10, help="Number of files to sample")
@click.option("--seed", default=42, help="Seed for random number generation")
@click.option("--subset", default="subset.csv", help="Output file")
def step1(count: int = 10, seed: int = 42, subset: str = "subset.csv"):
    rand = DeterministicRNG(seed)
    dataset = load_dataset()

    files = rand.sample(list(dataset.values()), count)

    # sort by hash
    files.sort(key=lambda x: x.sha1)

    records = []

    for i, row in enumerate(files):
        print(f"# {row.sha1} {row.meta.company_name}")
        # flatten into a dict

        meta = row.meta.model_dump()
        # drop period
        meta.pop('end_of_period')

        records.append(
            dict(
                sha1=row.sha1,
                cur=row.main_currency(),
                **meta  # all the other fields
            )
        )

    pd.DataFrame(records).to_csv(subset, index=False)


def ask_indicator_compare(rand: DeterministicRNG, df: pd.DataFrame) -> Optional[Question]:
    # only companies that have financial metric
    grouped = df[df['has_financial_performance_indicators']].groupby('cur').filter(lambda x: len(x) >= 3)
    # currency for them
    cur = rand.choice(list(grouped['cur'].unique()))
    # and pick 3 companies with that currency
    companies = rand.sample(list(grouped[grouped['cur'] == cur]['company_name']), 5)
    company_list = ", ".join(f'"{c}"' for c in companies)

    # generate questions
    ref = rand.choice(["highest", "lowest"])
    metric = rand.choice(["total revenue", "net income", "total assets"])
    question = f"Which of the companies had the {ref} {metric} in {cur} at the end of the period listed in annual report: {company_list}? If data for the company is not available, exclude it from the comparison. If only one company is left, return this company."

    return Question(text=question, kind="name")


def ask_fin_metric(rand: DeterministicRNG, df: pd.DataFrame) -> Optional[Question]:
    """
    Generate a question asking for a common financial KPI from the annual report.
    Returns a Question object with the schema set to "number".
    """

    company = rand.choice(list(df['company_name']))
    cur = df[df['company_name'] == company]['cur'].iloc[0]

    # A list of common financial KPIs that can be verified from an annual report
    financial_metrics = [
        f"Total revenue (in {cur})",
        f"Operating income (in {cur})",
        f"Net income (in {cur})",
        f"Gross margin (%)",
        f"Operating margin (%)",
        f"EPS (earnings per share) (in {cur})",
        f"EBITDA (in {cur})",
        f"Capital expenditures (in {cur})",
        f"Cash flow from operations (in {cur})",
        f"Long-term debt (in {cur})",
        f"Shareholders' equity (in {cur})",
        f"Dividend per share (in {cur})",
    ]

    metric = rand.choice(financial_metrics)

    question_variations = [
        f"What was the {metric} for {company} according to the annual report (within the last period or at the end of the last period)? If data is not available, return 'N/A'.",
        f"According to the annual report, what is the {metric} for {company}  (within the last period or at the end of the last period)? If data is not available, return 'N/A'.",
    ]

    question = rand.choice(question_variations)

    return Question(text=question, kind="number")


def ask_latest_merger_entity(rand: DeterministicRNG, df: pd.DataFrame) -> Optional[Question]:
    # pick one company with mentions_recent_mergers_and_acquisitions
    company = rand.choice(list(df[df['mentions_recent_mergers_and_acquisitions']]['company_name']))

    questions = [
        Question(
            text=f"What was the latest merger or acquisition that {company} was involved in? Return name of the entity or 'N/A'",
            kind="name"),
        # boolean
        Question(text=f"Did {company} mention any mergers or acquisitions in the annual report? If there is no mention, return False.", kind="boolean"),
    ]

    return rand.choice(questions)


def ask_about_compensation(rand: DeterministicRNG, df: pd.DataFrame) -> Optional[Question]:
    # pick one company with has_executive_compensation
    company = rand.choice(list(df[df['has_executive_compensation']]['company_name']))
    currency = df[df['company_name'] == company]['cur'].iloc[0]
    question = f"What was the largest single spending of {company} on executive compensation in {currency}? If data is not available in this currency, return 'N/A'."
    return Question(text=question, kind="number")


def ask_about_leadership_changes(rand: DeterministicRNG, df: pd.DataFrame) -> Optional[Question]:
    # pick company with changes
    company = rand.choice(list(df[df['has_leadership_changes']]['company_name']))

    questions = [
        Question(text=f"What are the names of all executives removed from their positions in {company}?", kind="names"),
        Question(text=f"What are the names of all new executives that took on new leadership positions in {company}?",
                 kind="names"),
        Question(
            text=f"Which leadership **positions** changed at {company} in the reporting period? If data is not available, return 'N/A'. Give me the title of the position.",
            kind="names"),
        # boolean
        Question(text=f"Did {company} announce any changes to its executive team in the annual report? If there is no mention, return False.",
                 kind="boolean"),

    ]

    return rand.choice(questions)


def ask_layoffs(rand: DeterministicRNG, df: pd.DataFrame) -> Optional[Question]:
    """
    Asks about layoffs if 'has_layoffs' is True.
    """
    eligible = df[df['has_layoffs'] == True]['company_name']
    if len(eligible) == 0:
        return None

    company = rand.choice(list(eligible))
    question_variations = [
        f"How many employees were laid off by {company} during the period covered by the annual report? If data is not available, return 'N/A'.",
        f"What is the total number of employees let go by {company} according to the annual report? If data is not available, return 'N/A'."
    ]
    question = rand.choice(question_variations)
    return Question(text=question, kind="number")


# product launches
def ask_about_product_launches(rand: DeterministicRNG, df: pd.DataFrame) -> Optional[Question]:
    # pick company with changes
    company = rand.choice(list(df[df['has_new_product_launches']]['company_name']))

    questions = [
        Question(text=f"What are the names of new products launched by {company} as mentioned in the annual report?",
                 kind="names"),
        Question(text=f"What is the name of the last product launched by {company} as mentioned in the annual report?",
                 kind="name"),
        # boolean
        Question(text=f"Did {company} announce any new product launches in the annual report? If there is no mention, return False.", kind="boolean"),
    ]

    return rand.choice(questions)


def ask_metadata_boolean(rand: DeterministicRNG, df: pd.DataFrame) -> Optional[Question]:
    question_templates = {
        "has_regulatory_or_litigation_issues": "Did {company} mention any ongoing litigation or regulatory inquiries?",
        "has_capital_structure_changes": "Did {company} report any changes to its capital structure?",
        "has_share_buyback_plans": "Did {company} announce a share buyback plan in the annual report?",
        "has_dividend_policy_changes": "Did {company} announce any changes to its dividend policy in the annual report?",
        "has_strategic_restructuring": "Did {company} detail any restructuring plans in the latest filing?",
        "has_supply_chain_disruptions": "Did {company} report any supply chain disruptions in the annual report?",
        "has_esg_initiatives": "Did {company} outline any new ESG initiatives in the annual report?",
    }

    field, template = rand.choice(list(question_templates.items()))

    # pick all companies with this field
    eligible = df[df[field] == True]['company_name']
    if len(eligible) == 0:
        return None

    company = rand.choice(list(eligible))
    question_text = template.format(company=company) + " If there is no mention, return False."
    return Question(text=question_text, kind="boolean")


def ask_industry_metric(rand: DeterministicRNG, df: pd.DataFrame) -> Optional[Question]:
    company = rand.choice(df['company_name'])
    industry = df[df['company_name'] == company]['major_industry'].iloc[0]

    industry_metrics = {
        "Technology": [
            "Number of patents at year-end",
            "Total capitalized R&D expenditure",
            "Total expensed R&D expenditure",
            "End-of-year tech staff headcount",
            "End-of-year total headcount",
            "Annual recurring revenue (ARR)",
            "Total intangible assets (IP valuation)",
            "Number of active software licenses",
            "Data center capacity (MW)",
            "Data center capacity (sq. ft.)",
            "Cloud storage capacity (TB)",
            "End-of-period market capitalization",
            "Year-end customer base",
            "Year-end user base"
        ],
        "Financial Services": [
            "Total assets on balance sheet at year-end",
            "Total deposits at year-end",
            "Loans outstanding at year-end",
            "Assets under management (AUM)",
            "Non-performing loan ratio (NPL) at year-end",
            "Tier 1 capital ratio at year-end",
            "Number of customer accounts at year-end",
            "Branch count at year-end",
            "End-of-year net interest margin (NIM)",
            "Return on equity (ROE) at year-end"
        ],
        "Healthcare": [
            "Number of hospital beds at year-end",
            "Number of owned clinics at year-end",
            "Number of managed clinics at year-end",
            "Active patient count (registered patients)",
            "Value of medical equipment (balance sheet)",
            "End-of-year bed occupancy rate",
            "Number of healthcare professionals on staff",
            "Number of laboratories at year-end",
            "Number of diagnostic centers at year-end",
            "Healthcare plan memberships (if applicable)",
            "Outstanding insurance claims (if applicable)",
            "R&D pipeline (number of therapies in phases)"
        ],
        "Automotive": [
            "Vehicle production capacity (units/year)",
            "Inventory of finished vehicles at year-end",
            "Global dealership network size",
            "Number of electric models available",
            "Number of hybrid models available",
            "Battery production capacity (if applicable)",
            "End-of-year automotive patent portfolio",
            "End-of-period market share (by units sold)",
            "Number of EV charging stations in network",
            "Year-end fleet average CO₂ emissions",
            "R&D workforce headcount"
        ],
        "Retail": [
            "Number of stores at year-end",
            "Total store floor area (sqm)",
            "Total store floor area (sq. ft.)",
            "Value of inventory on hand at year-end",
            "Number of distribution centers at year-end",
            "Number of fulfillment centers at year-end",
            "Loyalty program membership at year-end",
            "Online active customer accounts",
            "E-commerce active customer accounts",
            "Year-end store employee headcount",
            "Private label SKUs in portfolio",
            "Number of new store openings (cumulative in year)",
            "Online order fulfillment capacity (daily)"
        ],
        "Energy and Utilities": [
            "Total power generation capacity (MW)",
            "Number of power plants at year-end",
            "Number of facilities at year-end",
            "Percentage of renewable energy capacity",
            "Transmission network length",
            "Distribution network length",
            "Total number of customers connected",
            "Proven oil reserves (if applicable)",
            "Proven gas reserves (if applicable)",
            "Refinery throughput capacity",
            "Pipeline network length",
            "Greenhouse gas emissions intensity (CO₂/MWh)",
            "Year-end weighted average cost of energy production"
        ],
        "Hospitality": [
            "Number of properties at year-end",
            "Number of hotels at year-end",
            "Total number of rooms available",
            "Year-end occupancy rate",
            "Average daily rate (ADR) at final period",
            "Revenue per available room (RevPAR) at final period",
            "Loyalty program membership at year-end",
            "Number of restaurants",
            "Number of bars",
            "Conference/banquet space capacity (sq. ft.)",
            "Franchise agreements in force",
            "Hospitality workforce headcount"
        ],
        "Telecommunications": [
            "Mobile subscriber base at year-end",
            "Broadband subscriber base at year-end",
            "Mobile coverage area (population %)",
            "Mobile coverage area (geography %)",
            "Number of broadband subscribers",
            "Number of fiber subscribers",
            "Fiber network length (km)",
            "Fiber network length (miles)",
            "Average revenue per user (ARPU) at year-end",
            "5G coverage ratio (population %)",
            "Data center capacity (MW)",
            "Data center capacity (racks)",
            "Number of retail stores",
            "Number of service stores",
            "Network downtime (hours) in final reporting period"
        ],
        "Media & Entertainment": [
            "Number of streaming platform subscribers",
            "Number of online platform subscribers",
            "Broadcast coverage area (population reach)",
            "Advertising inventory at year-end",
            "Number of active licensing deals",
            "Size of film/TV content library (hours)",
            "Size of film/TV content library (titles)",
            "Social media follower count (all platforms)",
            "Year-end box office market share (if applicable)",
            "Number of production facilities",
            "In-house production capacity (titles/year)",
            "Headcount for creative roles",
            "Headcount for production roles"
        ],
        "Pharmaceuticals": [
            "Number of drugs on the market (approved)",
            "Number of compounds in Phase I",
            "Number of compounds in Phase II",
            "Number of compounds in Phase III",
            "Manufacturing capacity (units/year)",
            "Manufacturing capacity (liters/year)",
            "Global distribution network (markets served)",
            "Number of active pharmaceutical patents",
            "Clinical trial sites operating at year-end",
            "Inventory of active pharmaceutical ingredients",
            "Size of sales force (year-end)",
            "Pharmacovigilance reports (adverse events logged)",
            "Branded product count",
            "Generic product count"
        ],
        "Aerospace & Defense": [
            "Order backlog (value) at year-end",
            "Order backlog (units) at year-end",
            "Production capacity (aircraft/year)",
            "Production capacity (units/year)",
            "Number of defense contracts active",
            "Number of government contracts active",
            "R&D spending on advanced programs",
            "Number of employees with security clearance",
            "Military products in service (units)",
            "Defense products in service (units)",
            "Satellite capacity in orbit",
            "Spacecraft capacity in orbit",
            "Facilities footprint (sq. ft.)",
            "Facilities footprint (number of sites)",
            "Year-end patent portfolio (aerospace tech)",
            "Partnerships with government agencies at year-end"
        ],
        "Transport & Logistics": [
            "Fleet size (vehicles) at year-end",
            "Fleet size (aircraft) at year-end",
            "Fleet size (vessels) at year-end",
            "Warehouse capacity (sq. ft.)",
            "Warehouse capacity (cubic ft.)",
            "Number of distribution hubs",
            "Global route coverage (countries served)",
            "Global route coverage (regions served)",
            "Final-period on-time delivery rate",
            "Freight volume capacity (TEU)",
            "Freight volume capacity (tons)",
            "Fuel consumption rate (liters/year)",
            "Fuel consumption rate (per mile)",
            "CO₂ emissions from operations (ton/year)",
            "Year-end logistics staff headcount",
            "Infrastructure investments completed in the period"
        ],
        "Food & Beverage": [
            "Production capacity (e.g., bottling liters/hour)",
            "Number of manufacturing plants",
            "Number of warehouses in distribution network",
            "Number of depots in distribution network",
            "SKU count in portfolio",
            "Raw material supply contracts",
            "Inventory of raw materials at year-end",
            "Number of company-owned outlets",
            "Number of franchised outlets",
            "Year-end market share (by product category)",
            "Food safety certifications (sites certified)",
            "Brand portfolio size (distinct brands at year-end)"
        ]
    }

    metric = rand.choice(industry_metrics[industry])

    question_variatons = [
        f"What was the value of {metric} of {company} at the end of the period listed in annual report? If data is not available, return 'N/A'.",
        f"For {company}, what was the value of {metric} at the end of the period listed in annual report? If data is not available, return 'N/A'."]

    question = rand.choice(question_variatons)

    return Question(text=question, kind="number")


@cli.command()
@click.option("--count", default=10, help="Number of questions to generate")
@click.option("--seed", default=42, help="Seed for random number generation")
@click.option("--subset", default="subset.json", help="Subset of files")
@click.option("--questions", default="questions.json", help="Output file")
def step2(count: int = 10, seed: int = 42, subset: str = "subset.csv", questions: str = "questions.json"):
    rng = DeterministicRNG(seed)

    df = pd.read_csv(subset)

    results = []

    while len(results) < count:

        generators = [
            ask_indicator_compare,
            ask_latest_merger_entity,
            ask_industry_metric,
            ask_industry_metric,  # twice for more cases
            ask_industry_metric,
            ask_fin_metric,
            ask_fin_metric,
            ask_about_compensation,
            ask_about_leadership_changes,
            ask_about_product_launches,
            ask_metadata_boolean,
            ask_layoffs,
        ]

        try:
            question = rng.choice(generators)(rng, df)
            if question and question.text not in [q.text for q in results]:
                print(question.text)
                results.append(question)
        except Exception as e:
            raise
            print(e)
            continue

    with open(questions, "w") as f:
        json.dump([q.model_dump() for q in results], f, indent=2)


@cli.command()
@click.option("--limit", default=100, help="Number of random numbers to generate")
@click.option("--count", default=100, help="Number of iterations")
@click.option("--seed", default=42, help="Seed for random number generation")
def test_rng(limit: int = 100, count: int = 100, seed: int = 42):
    rng = DeterministicRNG(seed)
    # make array of 100
    arr = [0] * limit

    for i in range(count):
        arr[rng.random(limit)] += 1

    print(arr)


if __name__ == "__main__":
    cli()
