# Venture Studio Template

Template repository for new open source ventures created by the `Open Source Venture Studio`.

This repo is intentionally small. It exists to give each new venture a clean
starting point without dragging old project baggage into new work.

## What this template includes

- `README.md` for product framing and setup
- `LICENSE`
- `CONTRIBUTING.md`
- issue templates for venture briefs and build sprints
- PR template for disciplined shipping

## Studio repo policy

- One repo per venture or clearly bounded product context
- Research can happen without a repo
- Build-stage work should start in a dedicated repo
- Do not reuse unrelated legacy repos for new ventures

## How to use

Create a new public repo from this template:

```bash
gh repo create pcaarvalho/your-new-venture --public --template pcaarvalho/venture-studio-template
```

Then clone it and replace the placeholders:

- venture name
- wedge
- ICP
- first release scope
- owner

## First-day checklist

1. Rewrite the README for the specific venture.
2. Record the wedge, user, and testable promise.
3. Open the first build sprint issue.
4. Ship the smallest public milestone in 7 days or less.
