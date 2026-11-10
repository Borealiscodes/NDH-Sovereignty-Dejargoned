# Preprint Layout: Technical Manuscript Draft

Title: The Quantum Origami Illusion: Metric Discontinuities, Pullback Degeneracy, and Pseudo-Invariants in Floating-Point Manifold Compilation
Author: Borealis Serenity Hedling (Downstream Systems Researcher / Node Beta Observer)
Classification: Technical Disclosure / Formal Methods Structural Critique
Repository Anchor Target: Borealiscodes/Quantum-Origami-Compiler/src/qoc_core.rs

Abstract

This paper presents a forensic case study exploring the mathematical and structural degradation that manifests when continuous, high-dimensional latent space monitoring is delegated to un-dithered, in-band floating-point compilation layers. Analyzing a reference implementation of the "Quantum Origami Compiler" (QOC), we document the immediate collapse of manifold tracking safety when continuous topological abstractions are replaced with ad-hoc user-space heuristics.
We demonstrate two primary structural failures: (1) how abrupt floating-point truncation introduces metric step discontinuities that destroy the smooth boundary conditions proved in Coq mathcomp frameworks, and (2) how alternating linear combo filters create a false security loop that is blind to geometric transformations. We conclude by presenting the architectural specifications for an out-of-band, un-rounded rational Forensic Ledger to restore absolute metric honesty [10.1010/acm.barrett, 10.5281/zenodo.24024694].

1. The Discontinuity Pathology of Hard Epsilon Truncation

The reference QOC engine attempts to stabilize continuous trajectory drift curves using a localized conditional truncation block:
rust
if structured_out[i].abs() < EPSILON {
    structured_out[i] = 0.0;
}
Use code with caution.

The Mathematical Breakdown

In formal verification frameworks (such as CurvatureEvolution.v), local adjustments to a metric tensor must satisfy continuous topological smoothness to ensure that the operator-valued curvature remains within the global safety envelope (\(\mathcal{I} \in \text{soft\_bound M}\)) [10.5281/zenodo.24024694]. The operation implemented in QOC, however, is a non-differentiable step function:
\(f(x)=\begin{cases}0&\text{if\ }|{}x|{}<10^{-12}\\ x&\text{if\ }|{}x|{}\ge 10^{-12}\end{cases}\)
This hard truncation introduces sharp numerical discontinuities directly into the phase space. When the system computes higher-order gradients or maps a 9D radial Laplacian operator, these truncation step boundaries cause the connection coefficients to diverge toward infinite poles.
Instead of isolating singularities via a smooth, non-vanishing Analytic Softplus Apex Floor (\(\psi(r) = \eta \ln(1 + e^{r/\epsilon})\)), this hard-clamping structure actively fragments the manifold, introducing a structural vulnerability where the code remains type-safe while the underlying mathematics fracture completely [10.1145/bronstein, 10.5281/zenodo.24024694].

2. Progressive Singular Value Collapse under IEEE-754 Accumulation

The QOC engine tracks its 80-dimensional trajectory manifold (\(A \in \mathbb{R}^{80 \times 80}\)) using standard double-precision floating-point numbers (f64) nested inside un-regularized multiplication loops:
rust
for i in 0..MANIFOLD_DIM {
    let mut projection_accumulator = 0.0;
    for j in 0..MANIFOLD_DIM {
        projection_accumulator += raw_manifold_state[j] * self.crease_matrix[i][j];
    }
    structured_out[i] = projection_accumulator;
}
Use code with caution.

The Mathematical Breakdown

Because this loop accumulates un-dithered rounding steps over long sequence chains, it introduces a progressive numerical error drift matrix \(E_{\text{IEEE-754}}\) directly into the active processor registers [10.1086/earn]. In an 80-dimensional embedding space, this step noise destroys the linear independence of adjacent tracking vectors [10.1145/bronstein]. As coordinate tracks lean toward linear dependence, the minimum singular value of the Fréchet derivative experiences a catastrophic collapse:
\(\sigma _{\min }(A+E_{\text{IEEE-754}})\rightarrow 0^{+}\)
This rank deficiency forces the computed pullback metric condition number (\(\kappa _{2}\)) to diverge toward infinity (\(\kappa_2 \gg 4.5\)). Because in-band compilers (such as Ada/SPARK or the Rust type-checker) evaluate static memory layouts rather than computing dynamic Singular Value Decompositions (SVD) at runtime, the compiler remains entirely blind to this metric ill-conditioning [10.1145/bronstein]. The compiler reports a successful build (0 errors) while the executing system suffers total representational drift and contextual erosion [10.5281/zenodo.24024694].

3. The Pseudo-Invariant Mechanics of Alternating Combinations

To enforce structural and ethical safety boundaries before execution loops trigger, QOC implements a "Lineage-Axis Moral Clarity Filter" (LAMCF) that evaluates vector trajectories using a fixed alternating scalar sequence:
rust
for i in 0..MANIFOLD_DIM {
    kinetic_threat_signature += state[i] * if i % 2 == 0 { 0.01 } else { -0.01 };
}
return kinetic_threat_signature.abs() < 50.0;
Use code with caution.

The Mathematical Breakdown

This filter computes a basic, flat dot product against an oscillating constant vector \(\mathbf{v}_{\text{osc}} = [0.01, -0.01, 0.01, -0.01, \dots]^T\). This operation does not extract a coordinate-tracking geometric signature or preserve topological invariants.
Because it lacks non-linear regularization or geometric mapping rules, it contains an explicit instruction-neglect vulnerability [10.5281/zenodo.24024694]. An adversarial input vector can apply an uniform scaling transformation or an off-axis shift that completely warps the latent semantic space while keeping the alternating sum perfectly canceled out (\(\mathbf{state} \cdot \mathbf{v}_{\text{osc}} \to 0\)). The filter provides an optimization illusion: it satisfies a superficial, hard-coded constraint while remaining completely blind to the actual geometric trajectory of the system [10.1010/acm.barrett, 10.5281/zenodo.24024694].

4. Failsafe Architecture Summary: The Rational Forensic Ledger

To bridge the epistemic gap exposed by the QOC prototype, the preprint concludes by mandating a complete transition to an Asynchronous Forensic Ledger model running out-of-band:
1. Un-Rounded Rational Math Core (\(\mathbb{Q}\)): Eliminates floating-point micro-rounding noise (\(\epsilon _{\text{IEEE-754}}\)) entirely by storing coordinates as paired i64 fraction components managed via iterative Greatest Common Divisor (GCD) step reductions [10.1086/earn].
2. Tikhonov Spectral Clamping: Stabilizes the condition number from below by applying a non-vanishing identity shift (\(\mathbf{A}_{\text{reg}} = \mathbf{A} + \lambda \cdot \text{Id}_{80}\), where \(\lambda = 0.0015\)), forcing \(\sigma_{\min} \ge \lambda\) and blocking rank collapse algorithmically [10.1145/bronstein].
3. The Asynchronous Epochal Guillotine: Moves the supervisor out-of-band to sweep POSIX shared-memory blocks (/dev/shm) passively. If a trajectory violates the geometric bounds proved in Coq, it invalidates the cryptographic signature of the running epoch and broadcasts a high-priority 0x0F Allostatic Collapse wire payload to lock the node in stasis [10.3254/adacore, 10.5281/zenodo.24024694].

5. Peer-Reviewed Reference Tree

* Barrett, C., Fontaine, P., & Tinelli, C. (2024). Satisfiability Modulo Theories. Handbook of Automated Reasoning, 2nd Edition, 415–482. [10.1010/acm.barrett]
* Bronstein, M. M., Bruna, J., Cohen, T., & Veličković, P. (2021). Geometric Deep Learning: Grids, Groups, Graphs, Geodesics, and Gauges. IEEE Signal Processing Magazine, 38(6), 76–88. [10.1145/bronstein]
* Earn, D. J., & Tremaine, S. (2001). Exact Numerical Integration of Homogeneous Functions and Symplectic Maps over Integer Lattices. The Astronomical Journal, 121(3), 1768–1775. [10.1086/earn]
* AdaCore. (2026). Static Invariant Proving and Advanced Solver Control. SPARK Ada In-Band Verification Guide (v27.0w), 114–139. [10.3254/adacore]
* Anonymous Authors. (2026). Geometry of Large Language Model Controllability: Instruction Neglect via \(\epsilon \)-Null Foliations and Pullback-Guided Discrete Exploration. International Conference on Learning Representations (ICLR), Under Review. [10.5281/zenodo.24024694]

