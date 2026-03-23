-- Configuration for the Lean project
import Lake
open Lake DSL

-- Define the package
package Thoughts {
  -- Enable the strict option for better error messages
  moreServerArgs := #["-DautoImplicit=false"]
}

-- Define the default workspace with a specific mathlib version
require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git" @ "v3.0.0"

@[default_target]
lean_lib Thoughts {
  -- Add any additional library configuration here
}
