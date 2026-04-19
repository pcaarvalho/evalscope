# Evalscope

`evalscope` is a local-first eval runner for LLM apps.

The first wedge is narrow on purpose:
- define small eval datasets in YAML or JSON
- run them locally against an OpenAI model or simulated outputs
- score each case with simple checks
- compare the current run against a baseline artifact

This is for engineers shipping prompts or agents who want a fast answer to:

> Did this change make my app better or worse?

## Why this exists

Most LLM eval tooling drifts toward platforms, dashboards, and heavy setup.
`evalscope` starts one level lower:

- files in repo
- local runs
- simple CLI
- artifacts you can diff

That keeps the first release useful in less than 10 minutes.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Quickstart

Run the bundled quickstart example:

```bash
evalscope run examples/quickstart.json
```

This works without an API key because the example uses `simulate_output` to
demonstrate the flow locally.

For a real model call, set `OPENAI_API_KEY` and remove `simulate_output` from
your cases.

## Example spec

```json
{
  "name": "support-triage",
  "provider": "openai",
  "model": "gpt-4.1-mini",
  "prompt_template": "Classify this support ticket: {input}",
  "cases": [
    {
      "id": "billing",
      "input": "I was charged twice this month.",
      "simulate_output": "billing",
      "checks": [
        {"type": "exact_match", "value": "billing"}
      ]
    }
  ]
}
```

## Commands

Run an eval spec and write an artifact:

```bash
evalscope run examples/quickstart.json
```

Run with a baseline comparison:

```bash
evalscope run examples/quickstart.json --baseline .evalscope/runs/your-baseline.json
```

Diff two existing artifacts:

```bash
evalscope diff .evalscope/runs/current.json .evalscope/runs/baseline.json
```

Use CI-style exit behavior:

```bash
evalscope run examples/quickstart.json --ci
```

## Current v0 scope

- OpenAI provider only
- YAML and JSON specs
- checks: `exact_match`, `contains`, `regex`
- local JSON run artifacts
- baseline vs current diff
- example specs for local experimentation

## Explicitly out of scope

- dashboards
- SaaS backend
- multi-user collaboration
- complex orchestration
- multi-provider abstraction

## Repo layout

- [`evalscope/`](/Users/pedro/evalscope/evalscope) core package
- [`examples/`](/Users/pedro/evalscope/examples) sample eval specs
- [`tests/`](/Users/pedro/evalscope/tests) unit tests

## Development

Run the tests:

```bash
python3 -m unittest discover -s tests -v
```
