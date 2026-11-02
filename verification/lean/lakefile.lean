import Lake
open Lake Pure

package ndh where
  version := "0.1.0"
  keywords := #["geometry", "verification"]

/-
  Corrected git repository targeting mathlib4.
  Uses a stable release branch compatible with the toolchain version.
-/
require mathlib from git
  "https://github.com" @ "v4.7.0"

@[default_target]
lean_lib NDH where
  srcDir := "."
  -- Explicitly registers all core, stability, symplectic, and manifold validation modules
  roots := #[
    `NDH.CoreTypes, 
    `NDH.StabilityBounds, 
    `NDH.SymplecticPreservation, 
    `NDH.ManifoldStability
  ]
