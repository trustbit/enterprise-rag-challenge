"""
This is a prototype of deterministic question generator to test RAG systems.

Given a seed number and a list of company names, it generates a list of questions.
It will always generate the same questions given the same seed and company names.
"""

from typing import List
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

    def choice(self, seq: List[str]) -> str:
        return seq[self.random(len(seq))]

    def sample(self, seq: List[str], k: int) -> List[str]:

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
    "What was the {financial_metric} of {company} in {time_frame}?",
    "How much did {company} spend on {focus_area} in {time_frame}?",
    "What was the {ratio_or_metric} of {company} in {time_frame}?",
    "How many {count_metric} did {company} have in {time_frame}?",
    "What percentage of {company}'s {percentage_base} came from {segment_or_region} in {time_frame}?",
    "By what percentage did {company}'s {financial_metric} change from {year1} to {year2}?",
    "Which company had a higher {financial_metric}: {company1}, {company2} or {company3}, in {time_frame}?",
    "Did {company1} have a greater {ratio_or_metric} than {company2} in {time_frame}?",
    "How much more did {company1} spend on {focus_area} compared to {company2} in {time_frame}?",
    "Who is the {role} in the company {company}?"
]

# Define possible values for variables
parameters = {
    "company": ["Apple", "Microsoft", "Amazon", "Google", "Facebook", "Tesla", "Walmart", "JPMorgan Chase",
                "Johnson & Johnson", "Procter & Gamble"],
    "year": ["2019", "2020", "2021", "2022", "2023"],

    "quarter": [1, 2, 3, 4],
    "region": ["North America", "Europe", "Asia Pacific", "Latin America", "Middle East and Africa"],
    "country": ["USA", "China", "Germany", "Japan", "UK", "France", "Canada", "India", "Brazil", "Australia"],
    "segment": ["Cloud Services", "Consumer Products", "Enterprise Solutions", "Hardware", "Software",
                "Pharmaceuticals", "Automotive", "Financial Services", "E-commerce", "Advertising"],
    "financial_metric": ["total revenue", "net income", "total assets", "total liabilities", "shareholders' equity",
                         "goodwill", "intangible assets", "inventories", "accounts receivable", "accounts payable",
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
    "role": ["CEO", "CFO", "CTO", "COO", "CMO", "Board Chairman", "Chief Legal Officer",
              "Chief Human Resources Officer", "Chief Strategy Officer"]
}

SAMPLE_COMPANY_NAMES = ["Apple", "Microsoft", "Amazon", "Google", "Facebook", "Tesla", "Walmart", "JPMorgan Chase",
                        "Johnson & Johnson", "Procter & Gamble"]


@click.command()
@click.option("--questions", default=10, help="Number of questions to generate")
@click.option("--seed", default=42, help="Seed for random number generation")
@click.option("--company_names", help="Comma-separated list of company names to use")
def main(questions: int = 10, seed: int = 42, company_names: str = None):
    rand = DeterministicRNG(seed)

    if company_names:
        # company names match exactly annual reports
        # sort them alphabetically and drop duplicates
        companies = company_names.split(",")
        companies = list(sorted(set(companies)))
    else:
        companies = SAMPLE_COMPANY_NAMES

    for i in range(questions):
        # generate all args for this run
        args = {k: rand.choice(v) for k, v in parameters.items()}
        # company names should be different
        c1, c2, c3 = rand.sample(companies, 3)
        args['company1'] = c1
        args['company2'] = c2
        args['company3'] = c3

        template = rand.choice(templates)

        while "{" in template:
            template = template.format(**args)

        print(template)


if __name__ == "__main__":
    main()
