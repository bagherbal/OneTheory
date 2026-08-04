# `tests`

## Purpose

This directory guards the architecture and will later guard mathematical, physical, integration, and scientific behavior. Phase 0 tests enforce structure and dependency boundaries without implementing science.

## Belongs here

Architecture tests belong under `architecture`. Future unit tests cover promoted reusable components; scientific tests cover certified physical claims; integration tests cover direct compositions and unresolved dependency reporting.

## Does not belong here

The paper, standalone migration script, research-only experiments, measured observations, generated artifacts, or fabricated physical fixtures do not belong here. Tests must not make an open scientific result appear complete.

## Dependencies

Tests may inspect and import production code. They may not become production dependencies, and architecture tests may use standard-library AST inspection to enforce that rule.

## Promotion condition

Research code may be promoted only after a corresponding testable production contract exists, the result has an independent certificate and review, and tests validate the promoted implementation without relying on hidden research imports.
