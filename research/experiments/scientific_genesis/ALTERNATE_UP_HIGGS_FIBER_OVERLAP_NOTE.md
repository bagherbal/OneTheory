# Fiber-overlap transport of the strict alternate Hom class

The saved up-Higgs Hom cocycle has two right-chart syzygy vectors
\(s_\mu,s_\nu\) above each base chart, plus an overlap middle vector
\(g\) in Koszul degree zero and an overlap syzygy vector \(h\) in
Koszul summand `k1_u`. For the actual right mixed differential \(B_\nu\)
and the selected Schoen hypersurface equation \(F\), its projected
degree-two closure is the exact Laurent identity

\[
s_\mu-s_\nu+B_\nu g-Fh=0.
\]

The sign of \(Fh\) comes from the object degree of the syzygy-dual
summand. Dropping \(h\) does not give a closed overlap equation.

On the minor opens from the local-section calculation, write
\(B_\mu m_\mu=D_\mu s_\mu\) and
\(B_\nu m_\nu=D_\nu s_\nu\). The actual unipotent overlap gauge has
four entries \(q_i\). In Hom object order \((A,F0_0,\ldots,F0_3)\), it
sends the \(\mu\) numerator to the \(\nu\) frame by

\[
U(m_\mu)=(m_{\mu,A},
           m_{\mu,F0_0}-q_0m_{\mu,A},\ldots,
           m_{\mu,F0_3}-q_3m_{\mu,A}).
\]

The certified presentation comparison differs by the exact
hypersurface homotopy vector \(H\). Define

\[
N=D_\mu D_\nu g+D_\nu U(m_\mu)-D_\mu m_\nu,
\qquad
K=D_\nu(D_\mu h+H m_{\mu,A}).
\]

Then the actual arrow-derived matrix obeys \(B_\nu N=F K\) exactly.
Thus \(N/(D_\mu D_\nu)\) is right-resolution closed only after imposing
the hypersurface equation, with the explicit Koszul residual \(K\)
retained. The calculation checks all nine base/first-factor Čech
blocks. Their homogeneous numerator, denominator, and Koszul residual
agree exactly across all nine blocks, so the artifact stores one formula.

Equality of these homogeneous formulas is not a comparison through the
base-chart transition maps. This calculation does not glue different
base charts or different minor opens, nor establish the full Čech–Koszul Hom-to-tensor
chain map. An exterior-cone Higgs cocycle and Yukawa matrix remain
uncomputed.
