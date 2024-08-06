"""
This is a prototype of deterministic question generator to test RAG systems.

STEP1: Given a seed number, it will generate a subset of files to include in the test. This subset will
include SHA1 hashes of the files to ensure that the same files are used in the test. It will also include
the company name extracted from that PDF.

STEP2: Given the subset of files, it will generate a set of questions to ask about the companies
"""
import json
from pathlib import Path
from typing import List
import csv
import click


class DeterministicRNG:
    def __init__(self, seed: int):
        self.state = seed

    def random(self, n: int) -> int:
        # LCG parameters
        a, c, m = 1664525, 1013904223, 2 ** 32

        # Update state
        self.state = (a * self.state + c) % m

        # Return a number between 0 and n
        return self.state % n

    def choice(self, seq: List) -> str:
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


# Define question templates
templates = [
    ('What was the {fin_metric} of "{company}" in {time_frame}?', "number"),
    ('How much did "{company}" spend on {focus_area} in {time_frame}?', "number"),
    ('What was the {ratio_or_metric} of "{company}" in {time_frame}?', "number"),
    ('How many {count_metric} did "{company}" have in {time_frame}?', "number"),
    ('Which company had a higher {fin_metric}: "{company1}", "{company2}" or "{company3}", in {time_frame}?', "name"),
    ('Did "{company1}" have a greater {ratio_or_metric} than "{company2}" in {time_frame}?', "boolean"),
    ('How much more did "{company1}" spend on {focus_area} compared to "{company2}" in {time_frame}?', "number"),
    ('Who is the {role} in the company "{company}"?', "name"),
]

# Define possible values for variables
parameters = {
    "year": ["2021", "2022", "2023"],

    "quarter": [1, 2, 3, 4],
    "region": ["North America", "Europe", "Asia Pacific", "Latin America", "Middle East and Africa"],
    "country": ["USA", "China", "Germany", "Japan", "UK", "France", "Canada", "India", "Brazil", "Australia"],
    "segment": ["Cloud Services", "Consumer Products", "Enterprise Solutions", "Hardware", "Software",
                "Pharmaceuticals", "Automotive", "Financial Services", "E-commerce", "Advertising"],
    "fin_metric": ["total revenue", "net income", "total assets", "total liabilities", "shareholders' equity",
                        "intangible assets", "inventories", "accounts receivable", "accounts payable",
                         "operating cash flow", "free cash flow", "capital expenditures",
                         "research and development expenses", "marketing expenses", "acquisition costs"],
    "ratio_or_metric": ["earnings per share (EPS)", "Debt-to-Equity ratio", "Return on Equity (ROE)",
                        "Return on Assets (ROA)", "Quick Ratio", "Gross Profit Margin",
                        "Operating Margin", "Net Profit Margin", "market capitalization"],
    "count_metric": ["employees", "stores", "patents", "subsidiaries"],
    "percentage_base": ["total revenue", "total sales", "operating income", "net profit"],
    "segment_or_region": ["North America", "Europe", "Asia Pacific", "Latin America", "Middle East and Africa",
                          "Cloud Services", "Consumer Products", "Enterprise Solutions", "Hardware", "Software",
                          "Pharmaceuticals", "Automotive", "Financial Services", "E-commerce", "Advertising"],
    "external_entity": ["firm", "agency", "institution"],
    "action": ["spend", "invest", "allocate", "report", "disclose", "audit"],
    "focus_area": ["marketing", "sustainability initiatives", "risk management", "customer acquisition", "R&D"],
    "time_frame": ["the fiscal year {year}", "Q{quarter} {year}", "{date}", "the end of fiscal year {year}"],
    "date": ["December 31, {year}", "June 30, {year}"],
    "sustainability_metric": ["carbon emissions (in metric tons)", "water consumption (in cubic meters)",
                              "renewable energy usage (in percentage)", "waste reduction (in tons)"],
    "role": ["CEO", "CFO", "CTO", "COO", "CMO", "Board Chairman", "Chief Legal Officer"]
}


@click.group()
def cli():
    pass


def load_dataset() -> list[dict]:
    dataset = Path(__file__).parent / "dataset.csv"
    with open(dataset, "r") as file:
        # read the csv
        reader = csv.reader(file)
        rows = list(reader)

    return [dict(zip(rows[0], row)) for row in rows[1:]]


@cli.command()
@click.option("--count", default=10, help="Number of files to sample")
@click.option("--seed", default=42, help="Seed for random number generation")
@click.option("--subset", default="subset.json", help="Output file")
def step1(count: int = 10, seed: int = 42, subset: str = "subset.json"):
    rand = DeterministicRNG(seed)
    dataset = load_dataset()

    files = rand.sample(dataset, count)

    # sort by hash
    files.sort(key=lambda x: x['sha1'])

    for i, row in enumerate(files):
        print(f"# {row['sha1']} {row['name']}")

    with Path(subset).open("w") as file:
        json.dump(files, file, indent=2, ensure_ascii=False)


@cli.command()
@click.option("--count", default=10, help="Number of questions to generate")
@click.option("--seed", default=42, help="Seed for random number generation")
@click.option("--subset", default="subset.json", help="Subset of files")
def step2(count: int = 10, seed: int = 42, subset: str = "subset.json"):
    rand = DeterministicRNG(seed)

    with Path(subset).open("r") as file:
        rows = json.load(file)

    # pick company names
    companies = [row['name'] for row in rows]
    # add 15% of companies not in this subset, to test no answer
    extra_count = int(0.15 * count)
    extra = [row['name'] for row in rand.sample(load_dataset(), extra_count)]
    companies.extend(extra)

    parameters['company'] = companies

    selected = []

    for i in range(count):
        # generate all args for this run
        args = {k: rand.choice(v) for k, v in parameters.items()}
        # company names should be different
        c1, c2, c3 = rand.sample(companies, 3)
        args['company1'] = c1
        args['company2'] = c2
        args['company3'] = c3

        template, schema = rand.choice(templates)

        while "{" in template:
            template = template.format(**args)

        print(f"* {schema}: {template}")

        selected.append({"question": template, "schema": schema})


if __name__ == "__main__":
    cli()
