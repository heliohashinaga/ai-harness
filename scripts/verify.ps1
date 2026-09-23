#Requires -Version 7
<#
.SYNOPSIS
  Deterministic gate for the minimal harness: lint + tests.
#>
$ErrorActionPreference = "Stop"
uv run ruff check .
# Module invocation: bypasses .venv console-script shims (a corrupt
# pytest.exe trampoline once broke `uv run pytest` with no repo change).
uv run python -m pytest -q
