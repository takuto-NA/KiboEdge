# Interim Evaluation Report (2026-02-19)

## Scope

- Target runtime: LM Studio OpenAI-compatible endpoint `http://127.0.0.1:1234/v1`
- Target model: `lfm2-2.6b-exp`
- Metric: strict success rate (tool name and arguments match schema, executable in one pass)
- Case set size: 30 total
- Current progress: 5 / 30

## Safety Operating Mode

- Sequential execution only (no parallel tool/API execution)
- Per-request timeout: 12 seconds
- Evaluation default: small batch (`--max-cases` stepped up gradually)
- Cooldown between cases and early stop on consecutive request errors are enabled

## Test Results So Far

### Smoke Tests

- Parser smoke tests: PASS
- Schema validation smoke tests: PASS

### Incremental Evaluation Batches

1. `--max-cases 1`
   - total_cases: 1
   - successful_cases: 1
   - strict_success_rate: 1.0
   - failure_counts_by_reason: {}
   - result file: `logs/evaluations/evaluation_20260219T052450Z.json`

2. `--max-cases 2`
   - total_cases: 2
   - successful_cases: 2
   - strict_success_rate: 1.0
   - failure_counts_by_reason: {}
   - result file: `logs/evaluations/evaluation_20260219T052528Z.json`

3. `--max-cases 3`
   - total_cases: 3
   - successful_cases: 3
   - strict_success_rate: 1.0
   - failure_counts_by_reason: {}
   - result file: `logs/evaluations/evaluation_20260219T110805Z.json`

4. `--max-cases 4`
   - total_cases: 4
   - successful_cases: 4
   - strict_success_rate: 1.0
   - failure_counts_by_reason: {}
   - result file: `logs/evaluations/evaluation_20260219T110845Z.json`

5. `--max-cases 5`
   - total_cases: 5
   - successful_cases: 5
   - strict_success_rate: 1.0
   - failure_counts_by_reason: {}
   - result file: `logs/evaluations/evaluation_20260219T110930Z.json`

## Observations

- Strict success rate is stable at `1.0` for the first 5 cases under safe-mode settings.
- No failure reasons have been observed yet in completed batches.
- The stepped approach reduced risk after a prior machine crash event during heavier execution.

## Current Risk Notes

- Longer runs can still increase local resource pressure.
- Even with stable early batches, behavior may change in later case categories.
- Continue step-up strategy before attempting large batches.

## Recommended Next Steps

1. Continue incremental run: `--max-cases 6`, then `7`, then `8`.
2. Stop and inspect immediately if any failure reason appears (`parse_failure`, `schema_mismatch`, `request_error`).
3. After reaching 10 cases safely, run prompt-variant comparison with:
   - `python scripts/run_iteration_and_improve.py --max-cases 10 --request-timeout-seconds 12`
4. Keep all evaluation JSON outputs for before/after comparison.
