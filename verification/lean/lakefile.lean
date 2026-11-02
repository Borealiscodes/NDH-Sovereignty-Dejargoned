import Lake
open Lake Pure

package ndh where
  version := "0.1.0"
  keywords := #["geometry", "verification"]

require mathlib from git
  "https://github.com" @ "v4.7.0"

@[default_target]
lean_lib NDH where
  srcDir := "."
  roots := #[`NDH.CoreTypes, `NDH.StabilityBounds]
