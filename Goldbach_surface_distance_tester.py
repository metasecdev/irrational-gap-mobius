#!/usr/bin/env python3
"""
Goldbach Champion Surface Distance Tester
Scalable to n=100M+ (with enough RAM/time)

Usage:
    python goldbach_surface.py 10000000    # test n=10M
    python goldbach_surface.py 100000000   # test n=100M (takes longer)

Requirements:
    pip install sympy numpy heapq tqdm
"""

import math
import time
from heapq import heappush, heappop
from tqdm import tqdm
from sympy import primerange

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

def nordstrand_klein(theta, phi, scale=1.0):
    """Nordstrand figure-8 Klein bottle immersion (x,y,z)"""
    c  = math.cos(theta)
    s  = math.sin(theta)
    c2 = math.cos(phi / 2)
    s2 = math.sin(phi / 2)
    x = (2 + c2 * s - s2 * math.sin(2 * theta)) * c * scale
    y = (2 + c2 * s - s2 * math.sin(2 * theta)) * s * scale
    z = s2 * s + c2 * math.sin(2 * theta) * scale
    return (x, y, z)

def champion_surface_distance(
    n: int,
    max_small_p: int = None,
    top_k: int = 1000,
    verbose: bool = True
) -> tuple[float, list]:
    """
    Compute minimal surface distance for Goldbach pairs using champion config.
    Returns (min_distance, top_k_closest_pairs)
    """
    start_time = time.time()
    
    if n % 2 != 0 or n < 4:
        raise ValueError("n must be even and >= 4")
    
    # Use max_small_p to limit candidates (makes large n feasible)
    if max_small_p is None:
        max_small_p = n // 10
    
    print(f"[+] Sieving primes up to {n:,} ...")
    primes = list(primerange(2, n + 1))
    prime_set = set(primes)
    print(f"    Found {len(primes):,} primes  ({time.time() - start_time:.1f}s)")
    
    loglog_n = math.log(math.log(n + 2))
    
    # Champion parameters
    pulse_amp      = 0.18
    tilt_amp       = 0.12
    twist_period   = math.sqrt(math.log(n))
    z_shear_amp    = 0.08
    geodesic_scale = 0.80  # approximate shortening
    
    # Min-heap for top closest pairs: (dist, p, q)
    best_pairs = []
    
    # Progress bar over small primes
    small_primes = [p for p in primes if p <= max_small_p]
    print(f"[+] Checking {len(small_primes):,} candidates (p <= {max_small_p:,})")
    
    for p in tqdm(small_primes, desc="Progress", unit="pair"):
        q = n - p
        if q not in prime_set:
            continue
        
        # log-log fractions
        frac_p = math.log(math.log(p + 2)) / loglog_n
        frac_q = math.log(math.log(q + 2)) / loglog_n
        
        theta_p = 2 * math.pi * frac_p % (2 * math.pi)
        theta_q = 2 * math.pi * frac_q % (2 * math.pi)
        
        # Radial pulse
        radial = 1 + pulse_amp * math.sin(2 * math.pi * theta_p / twist_period)
        
        # Synchronized tilt
        tilt = tilt_amp * math.sin(radial)
        
        # Positions (two phase-shifted Klein immersions for double folding)
        pos_p1 = nordstrand_klein(theta_p, 0.5, radial)
        pos_q1 = nordstrand_klein(theta_q, 0.5, radial)
        pos_p2 = nordstrand_klein(theta_p + math.pi, 0.5, radial)  # phase shift
        pos_q2 = nordstrand_klein(theta_q + math.pi, 0.5, radial)
        
        # Average double folding
        pos_p = ((pos_p1[0] + pos_p2[0])/2,
                 (pos_p1[1] + pos_p2[1])/2,
                 (pos_p1[2] + pos_p2[2])/2)
        pos_q = ((pos_q1[0] + pos_q2[0])/2,
                 (pos_q1[1] + pos_q2[1])/2,
                 (pos_q1[2] + pos_q2[2])/2)
        
        # z-shear + tilt
        pos_p = (pos_p[0], pos_p[1], pos_p[2] + z_shear_amp * math.sin(theta_p) + tilt)
        pos_q = (pos_q[0], pos_q[1], pos_q[2] + z_shear_amp * math.sin(theta_q) + tilt)
        
        # Euclidean distance + geodesic correction
        dx = pos_p[0] - pos_q[0]
        dy = pos_p[1] - pos_q[1]
        dz = pos_p[2] - pos_q[2]
        dist = math.sqrt(dx*dx + dy*dy + dz*dz) * geodesic_scale
        
        heappush(best_pairs, (dist, p, q))
        if len(best_pairs) > top_k:
            heappop(best_pairs)
    
    runtime = time.time() - start_time
    print(f"[+] Done. Checked {len(small_primes):,} candidates in {runtime:.1f}s")
    
    if verbose and best_pairs:
        print("\nTop 10 closest Goldbach pairs (surface distance):")
        for dist, p, q in sorted(best_pairs)[:10]:
            print(f"  {p:10d} + {q:10d}   dist = {dist:.10f}")
    
    min_dist = best_pairs[0][0] if best_pairs else float('inf')
    return min_dist, sorted(best_pairs)

def plot_goldbach_pairs(pairs, output_path=None):
    if plt is None:
        raise RuntimeError("matplotlib is required to plot. Install with pip install matplotlib")
    if not pairs:
        raise ValueError("No pairs to plot")

    dists = [d for d, p, q in pairs]
    ps = [p for d, p, q in pairs]
    qs = [q for d, p, q in pairs]

    fig, ax = plt.subplots(figsize=(8, 5))
    scatter = ax.scatter(ps, dists, c=dists, cmap="viridis", label="p dist")
    ax.scatter(qs, dists, c="red", alpha=0.3, s=20, label="q dist")
    ax.set_xlabel("Prime component")
    ax.set_ylabel("Surface distance")
    ax.set_title("Goldbach Champion Surface Distances for top pairs")
    ax.legend()
    fig.colorbar(scatter, label="distance")
    fig.tight_layout()
    if output_path:
        fig.savefig(output_path, dpi=150)
        print(f"Saved plot to {output_path}")
    else:
        plt.show()


def save_pairs_csv(pairs, output_path):
    import csv
    if not pairs:
        print("No pairs to save")
        return
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["distance", "p", "q"])
        for dist, p, q in pairs:
            writer.writerow([f"{dist:.12f}", p, q])
    print(f"Saved top pairs to CSV: {output_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Goldbach champion surface distance tester")
    parser.add_argument("n", type=int, help="Even integer for Goldbach pair sum")
    parser.add_argument("--top-k", type=int, default=1000, help="Number of closest pairs to keep")
    parser.add_argument("--max-small-p", type=int, default=None, help="Limit small primes for candidate checking")
    parser.add_argument("--plot", action="store_true", help="Plot the top pairs using matplotlib")
    parser.add_argument("--plot-out", type=str, default=None, help="Save plot to file path (e.g. out.png)")
    parser.add_argument("--csv-out", type=str, default=None, help="Save top pairs to CSV file")
    args = parser.parse_args()

    print(f"\n=== Goldbach Champion Surface Test @ n = {args.n:,} ===\n")
    min_d, pairs = champion_surface_distance(
        args.n,
        max_small_p=args.max_small_p,
        top_k=args.top_k,
        verbose=True,
    )
    print(f"\nMinimal surface distance: {min_d:.10f}")
    print(f"Top {len(pairs)} closest pairs returned.")

    if args.plot:
        if plt is None:
            print("matplotlib is not installed; install it with pip install matplotlib to plot.")
        else:
            plot_goldbach_pairs(pairs, output_path=args.plot_out)

    if args.csv_out:
        save_pairs_csv(pairs, args.csv_out)
