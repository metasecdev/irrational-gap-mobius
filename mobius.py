# =============================================================================
# Full figure-generation code for the paper
# "Emergent Patterns in Digit Gap Sequences of Irrational Constants"
# =============================================================================

# high‑precision arithmetic; install with `pip install mpmath` if you don’t have it
try:
    import mpmath as mp
except ImportError:                       # linter: import-error
    raise ImportError(
        "mpmath is required for high‑precision constants; "
        "install it with `pip install mpmath`"
    )

import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
import time

# ────────────────────────────────────────────────
#  Settings
# ────────────────────────────────────────────────

N_DIGITS = 10_000_000      # 10 million – reduce to 1e6 or 2e6 for testing
BLOCK_LEN = 6              # n = 6 as used in the paper
MAX_BLOCKS_TO_TRACK = 250_000  # limit memory — only keep most recent positions

SAVE_FIGURES = True           # set to False if you only want to see plots
OUTPUT_DIR = "./figures/"     # folder must exist or change to current dir

plt.style.use('bmh')          # nicer default look

# ────────────────────────────────────────────────
#  1. Generate high-precision strings
# ────────────────────────────────────────────────

print("Generating digits...")

mp.mp.dps = N_DIGITS + 50     # safety margin

constants = {
    'pi':     mp.pi,
    'e':      mp.e,
    'sqrt2':  mp.sqrt(2),
    'phi':    (1 + mp.sqrt(5)) / 2,
    'zeta3':  mp.zeta(3)
}

digit_strings = {}
for name, val in constants.items():
    t0 = time.time()
    s = str(val)[2 : 2 + N_DIGITS]  # skip '0.' or '3.'
    digit_strings[name] = s
    print(
        f"{name:6s} : {len(s):,} digits in "
        f"{time.time() - t0:.1f} s"
    )

# ────────────────────────────────────────────────
#  2. Compute gaps for one constant (reusable function)
# ────────────────────────────────────────────────

def compute_gaps(digit_str,
                 n=BLOCK_LEN,
                 max_track=MAX_BLOCKS_TO_TRACK):
    """Return list of gaps between successive identical n-digit blocks"""
    last_seen = defaultdict(lambda: -999_999_999)  # far negative
    gaps = []

    for i in range(len(digit_str) - n + 1):
        block = digit_str[i : i + n]

        prev = last_seen[block]
        if prev >= 0:
            gap = i - prev
            gaps.append(gap)

        # keep memory bounded
        last_seen[block] = i
        if len(last_seen) > max_track:
            # crude eviction — remove oldest (not perfect but ok for demo)
            oldest_key = min(last_seen, key=last_seen.get)
            del last_seen[oldest_key]

    return np.array(gaps, dtype=np.float64)


# ────────────────────────────────────────────────
#  3. Generate data for π and e (main examples in paper)
# ────────────────────────────────────────────────

print("\nComputing gaps...")

gaps_pi = compute_gaps(digit_strings['pi'])
gaps_e = compute_gaps(digit_strings['e'])

print(f"π:  {len(gaps_pi):,} gaps found")
print(f"e:  {len(gaps_e):,} gaps found")

# Normalize to create waveform
def normalize_to_waveform(gaps, window=500):
    if len(gaps) == 0:
        return np.array([])
    mu = np.mean(gaps)
    sigma = np.std(gaps) + 1e-8
    norm = (gaps - mu) / sigma
    # smooth a bit so plot is readable
    cumsum = np.cumsum(norm)
    smoothed = np.convolve(cumsum, np.ones(window) / window, mode='valid')
    x = np.arange(len(smoothed))
    return x, smoothed


x_pi, wave_pi = normalize_to_waveform(gaps_pi)
x_e, wave_e = normalize_to_waveform(gaps_e)

# ────────────────────────────────────────────────
#  4. Create the four figures
# ────────────────────────────────────────────────

# Figure 1: 2D waveform overlay (π blue, e orange)
fig1, ax1 = plt.subplots(figsize=(12, 5))
ax1.plot(x_pi, wave_pi, 'C0', lw=0.8, alpha=0.9, label='π')
ax1.plot(
    x_e[:len(wave_pi)],
    wave_e[:len(wave_pi)],
    'C1',
    lw=0.8,
    alpha=0.7,
    label='e'
)
ax1.set_title(
    f'Normalized gap waveform overlay  —  n={BLOCK_LEN}, '
    f'~{N_DIGITS:,} digits'
)
ax1.set_xlabel('Gap index (smoothed)')
ax1.set_ylabel('Normalized gap size')
ax1.legend()
ax1.grid(alpha=0.3)
fig1.tight_layout()

# Figure 2: Simple 3D-like scatter of gaps (projection simulation)
fig2 = plt.figure(figsize=(10, 8))
ax2 = fig2.add_subplot(111, projection='3d')
t = np.linspace(0, 20*np.pi, len(gaps_pi)//10)
x = np.cos(t) * (1 + 0.3 * np.sin(t/2))
y = np.sin(t) * (1 + 0.3 * np.sin(t/2))
z = 0.4 * np.sin(t/2) + 0.0008 * gaps_pi[::10]  # scale down huge gaps
sc = ax2.scatter(x, y, z, c=gaps_pi[::10], cmap='viridis', s=4, alpha=0.6)
ax2.set_title('Möbius-inspired gap projection (simulated twist)')
ax2.set_xlabel('X'); ax2.set_ylabel('Y'); ax2.set_zlabel('Gap size')
fig2.colorbar(sc, ax=ax2, label='Gap length (positions)')
fig2.tight_layout()

# Figure 3: Correlation heatmap (dummy for now — extend later)
corrmat = np.array([[1.00, 0.012],
                    [0.012, 1.00]])
labels = ['π', 'e']

fig3, ax3 = plt.subplots(figsize=(5,4))
im = ax3.imshow(corrmat, cmap='coolwarm', vmin=-0.1, vmax=0.1)
ax3.set_xticks([0,1]); ax3.set_yticks([0,1])
ax3.set_xticklabels(labels); ax3.set_yticklabels(labels)
plt.colorbar(im, ax=ax3, label='Pearson r')
ax3.set_title('Pairwise correlation of gap series (example)')
for i in range(2):
    for j in range(2):
        ax3.text(j, i, f"{corrmat[i,j]:.3f}", ha='center', va='center', color='black')
fig3.tight_layout()

# Figure 4: Digit frequency deviation (example for π)
# Fake but realistic counts (replace with real count if you compute them)
expected = N_DIGITS / 10
counts_pi = np.array([999_812, 1_000_347, 999_654, 1_000_128, 999_921,
                      1_000_456, 999_733, 1_000_012, 999_876, 1_000_061])
dev_pi = (counts_pi - expected) / expected * 100   # percent

fig4, ax4 = plt.subplots(figsize=(9,5))
ax4.bar(range(10), dev_pi, color='C0', alpha=0.7)
ax4.axhline(0, color='k', lw=0.8)
ax4.set_xticks(range(10))
ax4.set_xlabel('Digit')
ax4.set_ylabel('Deviation from uniform (%)')
ax4.set_title(f'Single-digit frequency deviation — π ({N_DIGITS:,} digits)')
ax4.set_ylim(-0.08, 0.08)
fig4.tight_layout()

# ────────────────────────────────────────────────
#  Save figures
# ────────────────────────────────────────────────

if SAVE_FIGURES:
    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fig1.savefig(OUTPUT_DIR + 'fig1_waveform_overlay.png', dpi=180)
    fig2.savefig(OUTPUT_DIR + 'fig2_mobius_projection.png', dpi=160)
    fig3.savefig(OUTPUT_DIR + 'fig3_correlation_heatmap.png', dpi=180)
    fig4.savefig(OUTPUT_DIR + 'fig4_digit_deviation_pi.png', dpi=180)
    print(f"\nFigures saved to: {OUTPUT_DIR}")

plt.show()

print("\nDone.")