import mpmath as mp
import numpy as np
import matplotlib.pyplot as plt

mp.mp.dps = 50
alphas = [mp.pi, mp.e, mp.sqrt(2), (1+mp.sqrt(5))/2, mp.zeta(3)]

def simple_gap_wave(alpha, digits=100000, block_len=5):
    # placeholder: compute actual gaps here
    pass  # ← replace with real digit string + sliding window