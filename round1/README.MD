# Enterprise RAG Challenge with Annual Reports - Round 1
September 2024 by [Trustbit](https://www.trustbit.tech) (now a part of TIMETOACT GROUP as [TIMETOACT Austria](https://www.timetoact-group.at))

Copyright 2024 TIMETOACT Austria, licensed under Apache 2.0 license


## Instructions
**This is a friendly competition to test accuracy of different RAG systems in business workloads.**

We will start with question answering challenge.

Participants build a system that can answer questions about uploaded PDF documents (annual reports). Or they can test their existing AI Assistant system that is already built. 

Anybody can participate. Anonymous participation is also possible. All we ask - to share some details about your RAG implementation, for the benefit of the community. We would like to learn what works better in practice and share that with everybody.

When the competition comes:

1. Participants get in advance a set of annual reports as PDFs. They can take some time to process them.
2. List of questions for these files is generated. Within a few minutes (to avoid manual processing) participants will need to produce answers and upload them.
3. Afterwards the answers are checked in public and compiled into a public dataset.

All answers and data will be compiled into a public dataset. You will be able to compare performance of different teams and technologies (if team decided to answer a few questions) within a single table. We will also compile and publish a report at the end of the challenge.


*Frequently Asked Questions*

**Will you share all 46GB of Annual Report PDFs?**

No, we'll share only the competition subset as soon as it is known. These annual reports are public. If you really want, you can gather them on the internet.

**Why do questions include company names that are not included in PDFs?**

The purprose here is to detect hallucinations. If company data is not available in competition PDFs, then the RAG system must respond with `N/A` for the question.


**Why do some questions don't make sense?**

You will see questions that don't make sense, for example: 

* number: How many stores did "Strike Energy Limited" have in the end of fiscal year 2021?

Just like in the real world, not all questions make sense. If "Strike Energy Limited" didn't have any stores, the answer should be "N/A".

It is OK for many questions to ask about things that make sense on the surface, but be meaningless for the specific company or a document. A bad RAG system will hallucinate a plausible answer, a good RAG system will respond with "N/A".

**How do we verify correct answers?**

Trustbit will collect all answers first. We will then take time to review questions and manually come up with the correct answers. Correct answers will be published, along with the graded answers.

**I want to run a different challenge with tables, my language or industry. How I can do that?**

This repository is available publicly under the Apache 2.0 license, it can be used without restrictions. You can fork it, then:

1. Collect your own dataset of source files.
2. Adjust question generator to make sense for your domain.
3. Follow the overall process.

We only kindly ask to follow the rules of Apache 2.0 license in the process.



## Questions
Round one was a test run, to polish out the competition.

- PDF selection started on August 15th at 10:00 CET. See [pdfs](pdfs) 
- Question generation started at 12:00 CET. See  [questions.json](questions.json)

Seed generation outputs are below (see `round01` tag, if you want to reproduce)

Seed 1 (UTC time):

```text
856853 at 2024-08-15 08:05:07 (...eaa76b09)
# Deterministic seed: 3936840457
```

Seed 2 generation output (UTC time):

```text
# New block found! 856868 at 2024-08-15 10:05:01 (...2720eb96)
# Deterministic seed: 656468886
```


## Answers

Answer submissions are available in [submissions](submissions) folder.

"Correct" answers were derived manually, you can find them here: [answers.json](answers.json). I provided comments to explain each answer. 

Each answer is a list of tuples, each tuple is `(correct_answer, score)`. Sometimes it is possible that multiple answers were correct.

Due to the bias in the question generator at the test RUN, there were many questions with `N/A` answer. This made it possible to score really high by just having a system that responds `N/A` to every question. That's why for the round 1 we took a scoring system from the Math Kangaroo (international mathematics competition).





