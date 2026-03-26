import FinitistFramework_fixed

-- Simple test to verify the framework compiles
def test_compilation : Unit := ()

-- Test that we can reference the main theorem
example : FinitistFramework.pi_is_normal → True := fun _ => trivial

-- Test that we can reference the BBP definitions
example : Nat := FinitistFramework.gapSeq 0

-- Test that we can reference the quantum complexity definitions
example : FinitistFramework.GapWaveform 10 := sorry
