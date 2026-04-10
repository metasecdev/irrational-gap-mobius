import Mathlib.Data.Finset.Basic
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Basic
import Mathlib.Analysis.SpecialFunctions.Arsinh
import Mathlib.Analysis.Calculus.Deriv.Basic

open scoped BigOperators

namespace FinitistFramework

open Finset Real

/- ================================================
   BBP FORMULA FOR π
   ================================================ -/

/-- The BBP coefficient
    4/(8k+1) - 2/(8k+4) - 1/(8k+5) - 1/(8k+6). -/
def bbpCoeffR (k : Nat) : ℝ :=
  (4 : ℝ) / (8 * k + 1)
    - (2 : ℝ) / (8 * k + 4)
    - (1 : ℝ) / (8 * k + 5)
    - (1 : ℝ) / (8 * k + 6)

/-- The `k`-th real BBP summand for π. -/
def bbpSummandR (k : Nat) : ℝ :=
  bbpCoeffR k / ((16 : ℝ) ^ k)

/--
Mathematically correct BBP series statement for π.

I am stating this here as an axiom/theorem stub rather than pretending to provide
a complete formal proof from scratch.
-/
axiom pi_eq_bbp :
  π = ∑' k : Nat, bbpSummandR k

/-- Fractional part, written explicitly to avoid depending on a specific helper name. -/
def fracPart (x : ℝ) : ℝ :=
  x - Real.floor x

/--
Standard BBP digit-extraction quantity: the fractional part of `16^n * π`.

Its hexadecimal leading digit is the `n`-th hex digit after the point.
-/
def bbpHexShift (n : Nat) : ℝ :=
  fracPart ((16 : ℝ) ^ n * π)

/--
Mathematically correct digit-extraction statement:
the `n`-th hexadecimal digit of π is the floor of `16 * frac(16^n * π)`.

Again, this is the correct theorem statement, but not a full proof here.
-/
axiom bbp_hex_digit_theorem (n : Nat) :
  ∃ d : Nat,
    d < 16 ∧
    (d : ℝ) = Real.floor (16 * bbpHexShift n)

/- ================================================
   NONLINEAR BIJECTIVE TWIST
   ================================================ -/

/--
A genuinely nonlinear twist. Since `x ↦ x + k` is bijective and `Real.sinh`
is bijective on `ℝ`, this is bijective for every `k : Fin 3`.
-/
def twistK (k : Fin 3) (x : ℝ) : ℝ :=
  Real.sinh (x + (k : ℝ))

/-- Explicit inverse of the nonlinear twist. -/
def untwistK (k : Fin 3) (y : ℝ) : ℝ :=
  Real.arsinh y - (k : ℝ)

@[simp] lemma untwist_twist (k : Fin 3) (x : ℝ) :
    untwistK k (twistK k x) = x := by
  simp [untwistK, twistK]

@[simp] lemma twist_untwist (k : Fin 3) (y : ℝ) :
    twistK k (untwistK k y) = y := by
  simp [untwistK, twistK]

lemma twist_injective (k : Fin 3) :
    Function.Injective (twistK k) := by
  intro x y h
  have h' := congrArg (untwistK k) h
  simpa using h'

lemma twist_surjective (k : Fin 3) :
    Function.Surjective (twistK k) := by
  intro y
  refine ⟨untwistK k y, ?_⟩
  simp

lemma twist_bijective (k : Fin 3) :
    Function.Bijective (twistK k) := by
  exact ⟨twist_injective k, twist_surjective k⟩

/--
You can still define a gap index by flooring the nonlinear twist.
Using `Int.floor` is more natural on all of `ℝ`.
-/
def gapIndex (k : Fin 3) (x : ℝ) : Int :=
  Int.floor (twistK k x)

end FinitistFramework
