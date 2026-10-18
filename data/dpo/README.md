# WARNING: unsafe example data

`dpo_train_REJECTED_UNSAFE.jsonl` contains **deliberately dangerous advice**.
In each row, the `rejected` answer is wrong on purpose. It is a negative example
for DPO training (teaching a model what NOT to say).

- Do not show these answers to users.
- Do not use them as safety advice.
- The `chosen` answers are LLM-written and have not been reviewed by an expert.
  Do not treat them as verified safety advice either.

`train_for_pairs.jsonl` holds the training questions with their `chosen` answers only.
