# Phase 9 — LLM Reasoning & Auto-Remediation

## Goal
Use LLMs to explain incidents and propose safe, policy-compliant fixes and runbooks.

## Scope
- Retrieval context builder
- Prompt workflows for RCA and SQL suggestion
- Guardrails and policy checks

## Key Tasks
- Assemble retrieval context (logs, schema diffs, lineage, quality reports)
- Implement prompt templates for RCA and SQL patches
- Enforce guardrails to block unsafe SQL or broad-scoped changes
- Store suggestions with provenance and confidence
- Feedback loop for accepted/rejected suggestions

## Deliverables
- LLM interface + context assembler
- Policy/guardrail package
- Suggestion artifact schema and storage

## Exit Criteria
- Suggestions are grounded, policy-compliant, and reviewable
