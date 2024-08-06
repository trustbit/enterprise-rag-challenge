# Enterprise RAG Challenge with Annual Reports

by [Trustbit](https://www.trustbit.tech) (now a part of TIMETOACT GROUP as [TimeToAct Austria](https://www.timetoact-group.at))

> If you came here for the test run, just go to the [samples](samples) folder. It has PDFs and list of questions to be filled (in JSON format).


**This is a friendly competition to test accuracy of different RAG systems in business workloads.**

We will start with question answering challenge.

Participants build a system that can answer questions about uploaded PDF documents (annual reports). Or they can test their existing AI Assistant system that is already built. 

Anybody can participate. Anonymous participation is also possible. All we ask - to share some details about your RAG implementation, for the benefit of the community. We would like to learn what works better in practice and share that with everybody.

When the competition comes:

1. Participants get in advance a set of annual reports as PDFs. They can take some time to process them.
2. List of questions for these files is generated. Within a few minutes (to avoid manual processing) participants will need to produce answers and upload them.
3. Afterwards the answers are checked in public and compiled into a public dataset.



## Explanation

We have been discussing various approaches for building AI-driven assistants for companies. Most of the discussions focused on the efficiency and accuracy achieved by different approaches: RAG systems with vector databases and Domain-Driven AI Assistants (with Knowledge Maps).


In the long run, the technologies don’t even matter that much - they are just the implementation details. The only thing that is important - does the LLM-driven system provide accurate answers or does it hallucinate on the spot.

We can measure that! The idea started as a friendly competition challenge between a couple of teams.
Anybody interested can bring their own RAG system of choice into the game (or build one from scratch). This RAG should be able to ingest a bunch of public annual reports and answer questions.

All questions will be based on information retrieval tasks: “How many people are employed at the company X?”, “Which company has more liquidity?”, “Does the company X invest in green bonds?”

By the way, this test represents a real business case that is quite valuable for companies. First of all, here we can measure and compare the accuracy and hallucination rates of different approaches. Additionally, question answering over a large corpus of data maps well to cases like enterprise lead generation or internal customer support.

Participants can use any technology they wish to. It could be local, cloud-hosted or even third-party. The only requirements are:

- You can upload a test set of public annual reports.
- You can upload a list of questions to the system and get a list of answers.
- Between steps 1 and 2, there will be a lag of a few hours, so that the systems could ingest the data (e.g. compute embedding vectors or populate knowledge maps).
- There is no need to share the source code of the system.

If you are interested, below is the link for a sample subset of PDFs for development. Test dataset will obviously contain different PDFs.


## Geeky Details

We want to make the competition open and fair to everyone, so we invested extra effort in that.

All participants, even TimeToAct will be in the same conditions:

1. We share a list of all annual reports (7496 files and ~46GB) along with company names and file sha1 hashes in [dataset.csv](dataset.csv). These annual reports are public information. We don't share all these PDFs upfront, but if you really want, you can find them on the Internet.
2. We share a code that will generate next unpredictable random seed for the competition. It uses public blockchain API. See [gen_seed.py](gen_seed.py) for the implementation details.
3. We share the question generator that will randomly pick a subset of files for the competition. It will also generate random questions for these files. See [main.py](main.py).
4. Question generator uses a deterministic RNG that will work similarly for everybody.

Anybody can run this code at the moment of competition. Everybody is guaranteed to get the same list of files and questions for the competition at the same time. Nobody should be able to figure out these files and questions in advance.

As soon as we have a list of PDF files, TimeToAct will package them into a zip and share publicly. Everybody can verify sha1 hashes of these files to check that the files were not modified.


## Test Run

For verification, we did make a test run with 20 files and 40 questions.

You can find a list of files and questions in [samples](samples) folder. Below is the explanation of the process.

First, we waited for the next random seed:


```bash
python3 gen_seed.py
# Current block: 855626 at 2024-08-06 08:38:28. Waiting for new block...
# ..............New block found! 855627 at 2024-08-06 08:52:02
# Deterministic seed: 1836201229
```

Then we sampled dataset.csv for a list of 20 files using that seed:
```bash
python3 main.py step1 --seed=1836201229 --count=20            ~/tat/enterprise-rag
# 053b7cb83115789346e2a9efc7e2e640851653ff Global Medical REIT Inc.
# 3696c1b29566acc1eafc704ee5737fb3ae6f3d1d Zegona Communications plc
# 40b5cfe0d7bbf59e186492bfbe1b5002d44af332 Calyxt, Inc.
# 4b525836a5d7cb75489f6d93a3b1cf2b8f039bf2 TD SYNNEX
# 58a5f9f5c83159e63602b0b1dd27c27fb945c0e9 Eurocell PLC
# 608c5097dfc6e83505fd2259ad862dcec11a3f96 Sandwell Aquatics Centre
# 6b79f1c1de9d0e39a4576dcd4585849b9465b402 Mercurity Fintech Holding Inc.
# 71b04e0248ecf758990a0ab77bd69344be63bcf4 Motus GI Holdings, Inc.
# 99be213e4e689294ebae809bfa6a1b5024076286 Limbach Holdings, Inc.
# 9ae3bb21564a5098c4b4d6450655c22eff85deae Strike Energy Limited
# 9e703e719d94af786af5511c823ff86e9f04c070 Platform Technology
# 9ff4e041732c9841d5423e6ea0bbd6a0320df9ff VENUS METALS CORPORATION LIMITED
# bd5041c3e6909d92a7a88e4fb10dd8651df33228 NICE
# d734bac4a4815e616d84083ad4d3844655321215 Nykredit
# d81bbc64a4160b9946fea7a895f80e6201f52f27 Air Products
# dd78f748262b8ffa62de6484143ff55b38af24c7 Accuray Incorporated
# dfb1e552b18e116105d9125d9becafa443950e97 Kooth Plc
# e51b7204b91cbe7709bd3218e7d2d0c2b8dbb438 Ethernity Networks Ltd
# ea0757d27fa67cd347d9f046b939a911f5c9a08d Canadian Banc Corp.
# faf8d7d79152d61279eda1cfb58b8236ce2f82fa EMT
```

These files are uploaded to [samples](samples) folder. You can verify their hash using this code:

```py
import hashlib
from pathlib import PosixPath

def sha1_hash(file_path: PosixPath) -> str:
    sha1 = hashlib.sha1()
    with file_path.open('rb') as f:
        while chunk := f.read(8192):
            sha1.update(chunk)
```

Afterwards we waited for the next random seed:

```bash
python3 gen_seed.py
# New block found! 855628 at 2024-08-06 08:58:35
# Deterministic seed: 3031428637
```

Then we generated a list of questions using command:


```bash
python3 main.py step2 --seed=3031428637 --count=40
```

It generated questions like the ones below (full list is in [samples/questions.json](samples/questions.json)):

1. number: How much did "Accuray Incorporated" spend on risk management in Q2 2022?
2. name: Who is the CEO in the company "Zegona Communications plc"?
3. boolean: Did "Global Medical REIT Inc." have a greater Debt-to-Equity ratio than "Zegona Communications plc" in Q2 2021?
4. number: How many stores did "Accuray Incorporated" have in the end of fiscal year 2021?
5. number: How much did "Sandwell Aquatics Centre" spend on R&D in Q2 2023?
6. name: Who is the CFO in the company "EMT"?
7. boolean: Did "Calyxt, Inc." have a greater Return on Assets (ROA) than "Global Medical REIT Inc." in Q2 2023?

Note the schema specified for each question:

* number - only a metric number is expected as an answer. No decimal commas or separators. Correct: `122333`, incorrect: `122k`, `122 233`
* name - only name of the company is expected as an answer. It must be exactly as the name of the company in a dataset
* boolean - only `yes` or `no`

Important! Each schema also allows `N/A` ("Not Applicable") as an answer.