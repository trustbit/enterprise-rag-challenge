# Round 1 - Test Run


## Questions 

Round one was a test run, to polish out the competition.

- PDF selection started on August 15th at 10:00 CET. See [pdf](pdf) 
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

Answer submissions are available in [answers](answers) folder.

"Correct" answers were derived manually, you can find them here: [answers.json](answers.json). I provided comments to explain each answer. 

Each answer is a list of tuples, each tuple is `(correct_answer, score)`. Sometimes it is possible that multiple answers were correct.

Due to the bias in the question generator at the test RUN, there were many questions with `N/A` answer. This made it possible to score really high by just having a system that responds `N/A` to every question. That's why for the round 1 we took a scoring system from the Math Kangaroo (international mathematics competition).





