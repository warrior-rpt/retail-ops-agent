## Testing & Validation

This PoC includes lightweight evaluation focused on behavioral correctness rather than LLM text quality.

Validation covers:
- Deterministic risk routing (LOW / MEDIUM / HIGH)
- Correct graph path execution
- Human escalation only for HIGH-risk scenarios
- Alert suppression for non-critical cases

SNS interactions are mocked to ensure repeatable, side-effect-free testing.
