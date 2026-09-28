# Reciprocal covectors for the first-order Higgs action

Write the frozen first constituent as the Serre extension with A-line
`A₁=(-1,1,-1)` and determinant `L_E=(-2,2,0)`. The quotient line is
`B₁=L_E⊗A₁⁻¹=(-1,1,1)`, with the actual quotient landing in the
ideal subsheaf of B₁. The signed Hilbert–Burch minor row gives a global
map `q:E→B₁`: it annihilates both syzygy columns exactly, maps A to
zero, and therefore kills every constituent extension arrow. It is
a degree-zero map of the common Čech–Koszul resolution. No minor
denominator is inverted. Its orientation agrees with all six local
Plücker pairings against A.

Applying q to each saved outer-extension cochain gives actual
degree-one covectors

```text
q(eν) ∈ Hom(F,B₁),  ν=0,1.
```

The resulting full cycles have 16,515 and 13,779 terms. Their reduced
images are independent modulo exact boundaries. Thus one cannot
replace either by a primitive in this line-valued Hom complex.

The saved 324-term Higgs Hom representative has pure A output. Its
original orientation is `Hom(F⊗L_E,E)`, so the same cochain has the
exact orientation

```text
h ∈ Hom(F,A₁⊗L_E⁻¹) = Hom(F,B₁⁻¹).
```

Every object degree and ambient line degree agrees under this
retargeting; the full differential and nonboundary test remain exact.
The reciprocal covectors are not obtained by a local duality inverse
or by selecting an extension point.

This isolates a smaller target for the next computation. Their
signed derived exterior product has target `(Λ²F)*=L_E`, since
`B₁⊗B₁⁻¹=O` and `det F=L_E⁻¹`. The determinant endpoint is acyclic,
so the required degree-two action admits a degree-one primitive once
the actual product is constructed with the full totalization signs.
That product and primitive are **not yet computed**. Together with
the already-derived matter corrections, they must enter the complete
first-order scalar before any determinant coefficient is assigned.

The exact reciprocal-input construction is
`alternate_up_dual_higgs_inputs.py`. It removes a full Hom-to-tensor
inverse from this input preparation, not the missing Higgs action or
the eventual explicit exterior-cone representative.
