# lab — offline decision matrix CLI

Stdlib-only Python package `stack_lab` that prints comparison tables for AI engineering stacks.

```bash
export PYTHONPATH=src
python3 scripts/smoke_check.py
python3 -m stack_lab.cli layers
python3 -m stack_lab.cli compare frameworks
python3 -m stack_lab.cli compare all
python3 -m stack_lab.cli recommend "java spring enterprise rag with approval"
python3 -m unittest discover -s tests -v
```
