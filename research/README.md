# `research`

## Purpose

Research is the external workspace for unresolved investigations, exploratory calculations, and candidate derivations that are not yet promoted knowledge.

## Belongs here

Active work belongs under `experiments`. Each experiment should name its question, inputs, conventions, status, reproducibility command, and the production domain it may eventually inform.

## Does not belong here

Production implementations, hidden source inputs for generated results, final physical claims, paper chapter copies, or speculative bridges presented as interfaces do not belong here. Research must not be imported by production.

## Dependencies

Research may depend on production code and declared data, but it is outside the runtime package. Reverse imports are forbidden by the architecture tests.

## Promotion condition

An experiment may be promoted only after it yields a reproducible result, receives an independent mathematical or numerical certificate and scientific review, moves to its true production domain, and gains unit and scientific tests. No duplicate active implementation remains in research after promotion.
