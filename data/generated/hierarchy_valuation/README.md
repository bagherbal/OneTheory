# Hierarchy valuation artifacts

This directory stores deterministic outputs of
`research/experiments/hierarchy_valuation`. `line_sum_screen.json` is the
content-addressed gate-G3 screen of four-line SU(4) sums on the Schoen cover
in the box `|a|,|b|,|c| <= 4`. It records exact E2-page line cohomology,
every d2-ambiguous line left unresolved, every c1-trivial sum with 27 cover
families, and the (empty) set of sums with families in three distinct slots.

These are research artifacts, not physical carriers. Equivariant structures,
stability, Higgs content and Yukawa couplings are not constructed. Production
code must not import them, and no observation entered their computation.
Regenerate with
`python -m research.experiments.hierarchy_valuation.line_sum_screen`.

`line_sum_textures.json` classifies the leading 16.16.10 texture of every
27-family sum in that screen. Slot automorphisms force each leading coupling
to involve four distinct slots, so the only textures are the cross texture
(two unsuppressed families, one massless) and no leading Yukawa at all.
