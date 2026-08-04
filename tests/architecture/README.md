# Architecture tests

## Purpose

These tests define the Phase 0 structural contract: the exact layout, module docstring discipline, one-way production dependencies, and quiet import behavior.

## Belongs here

Layout checks, AST checks for production docstrings and forbidden implementation placeholders, import-graph checks, circular-import checks, and package-import checks belong here.

## Does not belong here

Scientific calculations, carrier data, numerical tolerances, physical matrices, paper claims, research experiments, or CLI tests do not belong here. These tests must not create APIs merely to make an architecture pass.

## Dependencies

Architecture tests inspect production files and may import the empty Phase 0 package. Production code must not import this directory or any other test code.

## Promotion condition

Research may be promoted into production only after these architectural tests continue to pass and domain-specific tests are added for the reviewed, certified result.
