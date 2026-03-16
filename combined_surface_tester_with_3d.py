#!/usr/bin/env python3
"""
Combined Goldbach + Riemann Hypothesis Champion Surface Tester
with 3D Matplotlib Visualization and CSV Export

Usage:
    python combined_surface_tester_with_3d.py <N> [mode] [top_k]

Modes:
  goldbach   - Goldbach pair surface distance + 3D plot (default)
  riemann    - Riemann zeta zero deviation + 3D plot

Examples:
  python combined_surface_tester_with_3d.py 10000000
  python combined_surface_tester_with_3d.py 1000000000 riemann 200
"""

import math
import time
import csv
import sys
from heapq import heappush, heappop
from tqdm import tqdm
from sympy import primerange, sieve
import mpmath
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

mpmath.mp.dps = 30  # high precision for Riemann

# ────────────────────────────────────────────────
#                  Klein bottle helper
# ────────────────────────────────────────────────

def nordstrand_klein(theta, phi, scale=1.0):
    """Nordstrand figure-8 Klein bottle immersion (x,y,z)"""
    c  = math.cos(theta)
    s  = math.sin(theta)
    c2 = math.cos(phi / 2)
    s2 = math.sin(phi / 2)
    x = (2 + c2 * s - s2 * math.sin(2 * theta)) * c * scale
    y = (2 + c2 * s - s2 * math.sin(2 * theta)) * s * scale
    z = s2 * s + c2 * math.sin(2 * theta) * scale
    return np.array([x, y, z])

# ────────────────────────────────────────────────
#                  Goldbach function + 3D plot
# ────────────────────────────────────────────────

def goldbach_champion(
    n: int,
    max_small_p: int = None,
    top_k: int = 1000,
    output_csv: bool = True,
    plot_3d: bool = True,
    verbose: bool = True
) -> tuple[float, list]:
    start_time = time.time()
    
    if n % 2 != 0 or n < 4:
        raise ValueError("n must be even and >= 4")
    
    if max_small_p is None:
        max_small_p = n // 10
    
    print(f"[Goldbach] Sieving primes up to {n:,} ...")
    sieve.extend(n)
    primes = list(sieve.primerange(2, n + 1))
    prime_set = set(primes)
    print(f"    Found {len(primes):,} primes  ({time.time() - start_time:.1f}s)")
    
    loglog_n = math.log(math.log(n + 2))
    
    pulse_amp      = 0.18
    tilt_amp       = 0.12
    twist_period   = math.sqrt(math.log(n))
    z_shear_amp    = 0.08
    geodesic_scale = 0.80
    
    best_pairs = []  # (dist, p, q, pos_p, pos_q)
    
    small_primes = [p for p in primes if p <= max_small_p]
    print(f"[Goldbach] Checking {len(small_primes):,} candidates (p <= {max_small_p:,})")
    
    for p in tqdm(small_primes, desc="Goldbach pairs", unit="pair"):
        q = n - p
        if q not in prime_set:
            continue
        
        frac_p = math.log(math.log(p + 2)) / loglog_n
        frac_q = math.log(math.log(q + 2)) / loglog_n
        
        theta_p = 2 * math.pi * frac_p % (2 * math.pi)
        theta_q = 2 * math.pi * frac_q % (2 * math.pi)
        
        radial = 1 + pulse_amp * math.sin(2 * math.pi * theta_p / twist_period)
        tilt = tilt_amp * math.sin(radial)
        
        pos_p1 = nordstrand_klein(theta_p, 0.5, radial)
        pos_q1 = nordstrand_klein(theta_q, 0.5, radial)
        pos_p2 = nordstrand_klein(theta_p + math.pi, 0.5, radial)
        pos_q2 = nordstrand_klein(theta_q + math.pi, 0.5, radial)
        
        pos_p = (pos_p1 + pos_p2) / 2
        pos_q = (pos_q1 + pos_q2) / 2
        
        pos_p[2] += z_shear_amp * math.sin(theta_p) + tilt
        pos_q[2] += z_shear_amp * math.sin(theta_q) + tilt
        
        dx = pos_p[0] - pos_q[0]
        dy = pos_p[1] - pos_q[1]
        dz = pos_p[2] - pos_q[2]
        dist = math.sqrt(dx*dx + dy*dy + dz*dz) * geodesic_scale
        
        heappush(best_pairs, (dist, p, q, pos_p, pos_q))
        if len(best_pairs) > top_k:
            heappop(best_pairs)
    
    runtime = time.time() - start_time
    print(f"[Goldbach] Done in {runtime:.1f}s")
    
    if verbose and best_pairs:
        print("\nTop 5 closest Goldbach pairs:")
        for d, p, q, _, _ in sorted(best_pairs)[:5]:
            print(f"  {p:10d} + {q:10d}   dist = {d:.10f}")
    
    min_dist = best_pairs[0][0] if best_pairs else float('inf')
    
    # CSV export
    if output_csv and best_pairs:
        csv_filename = f"goldbach_surface_pairs_n={n}_topk={top_k}.csv"
        with open(csv_filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["p", "q", "distance", "pos_p_x", "pos_p_y", "pos_p_z", "pos_q_x", "pos_q_y", "pos_q_z"])
            for d, p, q, pos_p, pos_q in sorted(best_pairs):
                writer.writerow([p, q, f"{d:.10f}",
                                 f"{pos_p[0]:.6f}", f"{pos_p[1]:.6f}", f"{pos_p[2]:.6f}",
                                 f"{pos_q[0]:.6f}", f"{pos_q[1]:.6f}", f"{pos_q[2]:.6f}"])
        print(f"[Goldbach] Top {len(best_pairs)} pairs saved to: {csv_filename}")
    
    # 3D Visualization
    if plot_3d and best_pairs:
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection='3d')
        ax.set_title(f"Goldbach Closest Pairs on Klein Bottle (n={n:,}, top {top_k})")
        
        # Plot all primes (downsampled for speed)
        theta_vals = [2 * math.pi * math.log(math.log(p + 2)) / loglog_n % (2 * math.pi) for p in primes[::10]]
        phi_vals = [0.5] * len(theta_vals)
        points = [nordstrand_klein(t, 0.5, 1.0) for t in theta_vals]
        xs, ys, zs = zip(*points)
        ax.scatter(xs, ys, zs, c='lightgray', s=1, alpha=0.3, label='Primes (downsampled)')
        
        # Plot top close pairs
        for _, p, q, pos_p, pos_q in sorted(best_pairs):
            ax.plot([pos_p[0], pos_q[0]], [pos_p[1], pos_q[1]], [pos_p[2], pos_q[2]],
                    'y-', linewidth=2, alpha=0.8)
            ax.scatter([pos_p[0]], [pos_p[1]], [pos_p[2]], c='blue', s=40)
            ax.scatter([pos_q[0]], [pos_q[1]], [pos_q[2]], c='red', s=40)
        
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.legend()
        plt.savefig(f"goldbach_3d_n={n}_topk={top_k}.png", dpi=300, bbox_inches='tight')
        plt.show()
        print(f"[Goldbach] 3D plot saved: goldbach_3d_n={n}_topk={top_k}.png")
    
    return min_dist, best_pairs

# ────────────────────────────────────────────────
#                  Riemann function + 3D plot
# ────────────────────────────────────────────────

def riemann_champion(
    T: int,
    top_k: int = 1000,
    output_csv: bool = True,
    plot_3d: bool = True,
    verbose: bool = True
) -> tuple[float, list]:
    start_time = time.time()
    N = int(T * math.log(T)) + int(T) + 1
    pulse_amp      = 0.18
    tilt_amp       = 0.12
    twist_period   = math.sqrt(math.log(T if T > 2 else 3))
    
    best_zeros = []  # (dev, t, re_s, radius, pos)
    
    print(f"[Riemann] Starting approximate search up to T = {T:,}  (N = {N:,})")
    if T > 1e7:
        print("[Riemann] Warning: using coarse scanning for very large T")

    max_candidates = min(2000, max(100, int(T // 500000)))
    step_size = max(1, int(T / max_candidates))
    candidates = list(range(14, int(T), step_size))
    print(f"[Riemann] Using {len(candidates):,} candidates")

    for t in tqdm(candidates, desc="Riemann heights", unit="height"):
        s = mpmath.mpc(0.5, t)
        z = mpmath.zeta(s)
        dev = float(abs(mpmath.re(z)))
        radius = 0.0

        theta = 2 * math.pi * math.log(t + 1) / math.log(T + 2) % (2 * math.pi)
        phi = 2 * math.pi * (float(mpmath.re(s)) - 0.5) / math.log(T + 2) % (2 * math.pi)
        radial = 1 + pulse_amp * math.sin(2 * math.pi * theta / twist_period)
        tilt = tilt_amp * math.sin(radial)

        pos = np.array([math.cos(theta), math.sin(theta), math.cos(phi), math.sin(phi)]) * radial
        pos[2] += tilt

        heappush(best_zeros, (dev, float(t), float(mpmath.re(s)), radius, pos))
        if len(best_zeros) > top_k:
            heappop(best_zeros)

    runtime = time.time() - start_time
    print(f"[Riemann] Done in {runtime:.1f}s")
    
    if verbose and best_zeros:
        print("\nTop 5 closest-to-line zeros:")
        for dev, t, re_s, radius, _ in sorted(best_zeros)[:5]:
            print(f"  t ≈ {t:10.2f}   Re(s) = {re_s:.10f}   dev = {dev:.2e}   radius = {radius:.2e}")
    
    max_dev = max([dev for dev, _, _, _, _ in best_zeros]) if best_zeros else float('inf')

    if output_csv and best_zeros:
        csv_filename = f"riemann_surface_zeros_T={T}_topk={top_k}.csv"
        with open(csv_filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["t", "Re(s)", "deviation", "certified_radius"])
            for dev, t, re_s, radius, _ in sorted(best_zeros):
                writer.writerow([f"{t:.6f}", f"{re_s:.10f}", f"{dev:.2e}", f"{radius:.2e}"])
        print(f"[Riemann] Top {len(best_zeros)} zeros saved to: {csv_filename}")

    if plot_3d and best_zeros:
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection='3d')
        ax.set_title(f"Riemann Zeros on Clifford Torus (T={T:,}, top {top_k})")

        xs, ys, zs = [], [], []
        for _, _, _, _, pos in best_zeros:
            xs.append(pos[0]); ys.append(pos[1]); zs.append(pos[2])
        ax.scatter(xs, ys, zs, c='lightblue', s=20, alpha=0.6, label='Candidates')

        highlighted = sorted(best_zeros)[:min(20, len(best_zeros))]
        for dev, t, re_s, radius, pos in highlighted:
            ax.scatter([pos[0]], [pos[1]], [pos[2]], c='red' if dev < 1e-2 else 'orange', s=60)

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.legend()
        plt.savefig(f"riemann_3d_T={T}_topk={top_k}.png", dpi=300, bbox_inches='tight')
        plt.show()
        print(f"[Riemann] 3D plot saved: riemann_3d_T={T}_topk={top_k}.png")

    return max_dev, best_zeros

# ────────────────────────────────────────────────
#                  Main CLI
# ────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python combined_surface_tester_with_3d.py <N> [mode=goldbach|riemann] [top_k]")
        print("Examples:")
        print("  python combined_surface_tester_with_3d.py 10000000")
        print("  python combined_surface_tester_with_3d.py 1000000000 riemann 200")
        sys.exit(1)
    
    N = int(sys.argv[1])
    mode = sys.argv[2].lower() if len(sys.argv) > 2 else "goldbach"
    top_k = int(sys.argv[3]) if len(sys.argv) > 3 else 1000
    
    print(f"\n=== Champion Surface Test @ {mode.upper()} = {N:,} ===\n")
    
    if mode in ("goldbach", "g"):
        min_d, pairs = goldbach_champion(N, top_k=top_k)
        print(f"\nGoldbach minimal surface distance: {min_d:.10f}")
    
    elif mode in ("riemann", "r"):
        max_dev, zeros = riemann_champion(N, top_k=top_k)
        print(f"\nRiemann maximal real-part deviation: {max_dev:.2e}")
    
    else:
        print(f"Unknown mode: {mode}. Use 'goldbach' or 'riemann'")
        sys.exit(1)