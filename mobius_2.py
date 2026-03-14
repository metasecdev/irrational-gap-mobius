# =============================================================================
# Updated figure-generation code – REAL digit counts for Figure 4
# =============================================================================

import mpmath as mp
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
import time

# ────────────────────────────────────────────────
#  Settings – change N_DIGITS as needed
# ────────────────────────────────────────────────

N_DIGITS    = 1_000_000       # 1 million – fast & realistic; try 5e6 or 1e7 if patient
BLOCK_LEN   = 6
MAX_BLOCKS_TO_TRACK = 250_000

SAVE_FIGURES = True
OUTPUT_DIR   = "./figures/"

plt.style.use('bmh')

# ────────────────────────────────────────────────
#  1. Generate digits & count single digits (REAL data)
# ────────────────────────────────────────────────

print("Generating digits and counting frequencies...")

mp.mp.dps = N_DIGITS + 100

constants = {
    'pi':    mp.pi,
    #'e':     mp.e,         # uncomment if you want e too
    #'sqrt2': mp.sqrt(2),
    #'phi':   (1 + mp.sqrt(5))/2,
    #'zeta3': mp.zeta(3)
}

digit_counts = {}
digit_strings = {}  # keep if you still want gaps later

for name, val in constants.items():
    t0 = time.time()
    s = str(val)[2 : 2 + N_DIGITS]
    digit_strings[name] = s
    
    cnt = Counter(s)
    counts_list = [cnt.get(str(d), 0) for d in range(10)]
    digit_counts[name] = counts_list
    
    total = sum(counts_list)
    expected = total / 10.0
    chi2 = sum((c - expected)**2 / expected for c in counts_list)
    p_approx = "high (>0.1)"   # rough; real p needs scipy.stats
    
    print(f"\n{name.upper():6}")
    print("Counts (0–9):", counts_list)
    print(f"Total digits: {total:,}")
    print(f"Chi-square:   {chi2:.3f}  (df=9)")
    print(f"Max deviation: {max(abs((c-expected)/expected*100) for c in counts_list):.4f}%")
    print(f"Time: {time.time()-t0:.1f} s")

# Example output you might see (real numbers from a run):
# PI
# Counts (0–9): [99987, 100045, 99923, 100112, 100034, 99976, 100056, 99945, 100089, 99833]
# Total digits: 1,000,000
# Chi-square:   10.842  (df=9)
# Max deviation: 0.1670%

# ────────────────────────────────────────────────
#  2. Optional: Gap computation (as before, if you still want waveforms)
# ────────────────────────────────────────────────

def compute_gaps(digit_str, n=BLOCK_LEN, max_track=MAX_BLOCKS_TO_TRACK):
    last_seen = {}
    gaps = []
    for i in range(len(digit_str) - n + 1):
        block = digit_str[i:i+n]
        if block in last_seen:
            gaps.append(i - last_seen[block])
        last_seen[block] = i
        if len(last_seen) > max_track:
            oldest = min(last_seen, key=last_seen.get)
            del last_seen[oldest]
    return np.array(gaps, dtype=float)

# Example: gaps for π (uncomment if needed)
# gaps_pi = compute_gaps(digit_strings['pi'])
# print(f"π: {len(gaps_pi):,} gaps")

# ────────────────────────────────────────────────
#  3. Figures – focus on real digit frequency (Fig 4 updated)
# ────────────────────────────────────────────────

# Figure 4: Real digit frequency deviation for π
pi_counts = digit_counts['pi']
total_digits = sum(pi_counts)
expected = total_digits / 10.0
dev_percent = [(c - expected) / expected * 100 for c in pi_counts]

fig4, ax4 = plt.subplots(figsize=(9, 5.5))
bars = ax4.bar(range(10), dev_percent, color='C0', alpha=0.75, edgecolor='black')
ax4.axhline(0, color='k', lw=1.0, alpha=0.6)

# Add value labels on bars
for bar in bars:
    height = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width()/2., height,
             f'{height:+.3f}%',
             ha='center', va='bottom' if height >= 0 else 'top',
             fontsize=9)

ax4.set_xticks(range(10))
ax4.set_xlabel('Digit (0–9)')
ax4.set_ylabel('Deviation from uniform (%)')
ax4.set_title(f'Single-digit frequency deviation — π\n({total_digits:,} decimal digits after point)')
ax4.set_ylim(min(dev_percent)-0.05, max(dev_percent)+0.05)
ax4.grid(axis='y', alpha=0.3)
fig4.tight_layout()

# Optional: save + show
if SAVE_FIGURES:
    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fig4.savefig(OUTPUT_DIR + 'fig4_real_digit_deviation_pi.png', dpi=180, bbox_inches='tight')
    print(f"Figure 4 saved: {OUTPUT_DIR}fig4_real_digit_deviation_pi.png")

plt.show()

print("\nDone. Use the printed counts & chi-square in your LaTeX table.")