#Requires -Version 7
<#
.SYNOPSIS
  Deterministic gate for the minimal harness: lint + tests.
#>
$ErrorActionPreference = "Stop"
uv run ruff check .
uv run pytest -q
