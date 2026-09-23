#Requires -Version 7
<#
.SYNOPSIS
  Collect a Verdict for a task, e.g.:
    .\scripts\evaluate.ps1 .factory\tasks\TASK-000-example.md
  Runs the deterministic gate, then prompts the fresh-context
  evaluation per agents\evaluator.md. Writes YAML to .factory\evaluations\.
#>
param([Parameter(Mandatory = $true)][string]$TaskFile)
$ErrorActionPreference = "Stop"
if (-not (Test-Path $TaskFile)) { throw "Task file not found: $TaskFile" }
.\scripts\verify.ps1
$stem = [IO.Path]::GetFileNameWithoutExtension($TaskFile)
"Deterministic gate passed for $stem."
"Next: judge from fresh context per agents\evaluator.md and write .factory\evaluations\$stem.yaml"
"Verdict starts FAIL. Only evidence flips a criterion to PASS."
