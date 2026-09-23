#Requires -Version 7
<#
.SYNOPSIS
  Start an Agent Session for a task file, e.g.:
    .\scripts\run.ps1 .factory\tasks\TASK-000-example.md
  The operator (you, in pi/Claude Code) IS the agent: read agents\agent.md,
  follow docs\workflow.md, update .factory\state\current.md as you go.
#>
param([Parameter(Mandatory = $true)][string]$TaskFile)
$ErrorActionPreference = "Stop"
if (-not (Test-Path $TaskFile)) { throw "Task file not found: $TaskFile" }
"Task: $TaskFile"
"1. Read agents\agent.md and the task file."
"2. Work the loop in docs\workflow.md (inspect -> edit -> test)."
"3. Record progress in .factory\state\current.md, then run .\scripts\verify.ps1."
