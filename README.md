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

Requires Python 3.10+. Clone the repo and run everything below from the repo
root:

```bash
git clone https://github.com/pcaarvalho/evalscope
cd evalscope
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Quickstart

Run the bundled quickstart example:

```bash
evalscope run examples/quickstart.json
```

Expected output looks like:

```text
Run written to: .evalscope/runs/<timestamp>-quickstart-local.json
Summary: 2/2 passed (0 failed, pass_rate=1.0)
```

This works without an API key because the example uses `simulate_output` to
demonstrate the flow locally.

Prefer YAML? The bundled YAML example exercises the same local flow:

```bash
evalscope run examples/support_triage.yaml
```

For a real model call, copy one of the bundled specs, set `OPENAI_API_KEY`,
and remove `simulate_output` from the cases you want to execute live.

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

The `.evalscope/runs/` directory is created automatically. If you want a stable
baseline path for repeat comparisons, write one explicitly:

```bash
evalscope run examples/quickstart.json --output .evalscope/runs/quickstart-baseline.json
```

Then compare a fresh run against that saved baseline:

```bash
evalscope run examples/quickstart.json --output .evalscope/runs/quickstart-current.json --baseline .evalscope/runs/quickstart-baseline.json
```

Diff two existing artifacts:

```bash
evalscope diff .evalscope/runs/quickstart-current.json .evalscope/runs/quickstart-baseline.json
```

Use CI-style exit behavior:

```bash
evalscope run examples/quickstart.json --ci
```

Check the installed CLI version:

```bash
evalscope --version
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

- `evalscope/` core package
- `examples/` sample eval specs
- `tests/` unit tests

## Development

Run the tests:

```bash
python3 -m unittest discover -s tests -v
```

The repo also includes a GitHub Actions workflow that installs the package,
runs the unit tests, and smoke-tests the bundled quickstart example.
