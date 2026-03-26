-- Configuration for the Lean project
import Lake
open Lake DSL

-- Define the package
package Thoughts {
  -- Enable the strict option for better error messages
  moreServerArgs := #["-DautoImplicit=false"]
}

-- Define the default workspace with mathlib
require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git"

@[default_target]
lean_lib Thoughts {
  -- Add any additional library configuration here
}
