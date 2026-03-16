#!/usr/bin/env python3
"""
Combined Goldbach + Riemann + Twin Prime Champion Surface Tester
with Klein Bottle Surface Mesh + 3D Visualization + CSV Export

Usage:
    python combined_surface_tester_with_mesh.py <N> [mode] [top_k]

Modes:
  goldbach    - Goldbach pairs (default)
  riemann     - Riemann zeros
  twinprime   - Twin primes (p and p+2)

Examples:
  python combined_surface_tester_with_mesh.py 10000000
  python combined_surface_tester_with_mesh.py 10000000 twinprime 500
  python combined_surface_tester_with_mesh.py 1000000 riemann 200
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

mpmath.mp.dps = 30

# ────────────────────────────────────────────────
#                  Klein bottle helpers
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

def plot_klein_bottle_mesh(ax, alpha=0.15, wire=True):
    """Add Klein bottle surface mesh to 3D axis"""
    theta = np.linspace(0, 2*np.pi, 40)
    phi   = np.linspace(0, 2*np.pi, 40)
    Theta, Phi = np.meshgrid(theta, phi)
    
    X = (2 + np.cos(Phi/2) * np.sin(Theta) - np.sin(Phi/2) * np.sin(2*Theta)) * np.cos(Theta)
    Y = (2 + np.cos(Phi/2) * np.sin(Theta) - np.sin(Phi/2) * np.sin(2*Theta)) * np.sin(Theta)
    Z = np.sin(Phi/2) * np.sin(Theta) + np.cos(Phi/2) * np.sin(2*Theta)
    
    if wire:
        ax.plot_wireframe(X, Y, Z, color='gray', alpha=alpha, linewidth=0.5)
    else:
        ax.plot_surface(X, Y, Z, color='lightgray', alpha=alpha, linewidth=0)

# ────────────────────────────────────────────────
#                  Goldbach function
# ────────────────────────────────────────────────

def goldbach_champion(n: int, top_k: int = 1000, output_csv: bool = True, plot_3d: bool = True):
    start_time = time.time()
    if n % 2 != 0 or n < 4:
        raise ValueError("n must be even and >=4")
    primes = list(primerange(2, n+1))
    prime_set = set(primes)
    loglog_n = math.log(math.log(n+2))
    pulse_amp=0.18
    tilt_amp=0.12
    twist_period=math.sqrt(math.log(n))
    z_shear_amp=0.08
    geodesic_scale=0.80
    best_pairs=[]
    max_small=n//10
    small_primes=[p for p in primes if p<=max_small]
    print(f"[Goldbach] Sieved {len(primes):,}, checking {len(small_primes):,} candidates")
    for p in tqdm(small_primes, desc="Goldbach", unit="pair"):
        q=n-p
        if q not in prime_set: continue
        frac_p=math.log(math.log(p+2))/loglog_n
        frac_q=math.log(math.log(q+2))/loglog_n
        theta_p=2*math.pi*frac_p%(2*math.pi)
        theta_q=2*math.pi*frac_q%(2*math.pi)
        radial=1+pulse_amp*math.sin(2*math.pi*theta_p/twist_period)
        tilt=tilt_amp*math.sin(radial)
        pos_p=nordstrand_klein(theta_p,0.5,radial)
        pos_q=nordstrand_klein(theta_q,0.5,radial)
        pos_p=(pos_p[0],pos_p[1],pos_p[2]+z_shear_amp*math.sin(theta_p)+tilt)
        pos_q=(pos_q[0],pos_q[1],pos_q[2]+z_shear_amp*math.sin(theta_q)+tilt)
        dx=pos_p[0]-pos_q[0]; dy=pos_p[1]-pos_q[1]; dz=pos_p[2]-pos_q[2]
        dist=math.sqrt(dx*dx+dy*dy+dz*dz)*geodesic_scale
        heappush(best_pairs,(dist,p,q,pos_p,pos_q))
        if len(best_pairs)>top_k: heappop(best_pairs)
    if output_csv and best_pairs:
        csv_filename=f"goldbach_surface_pairs_n={n}_topk={top_k}.csv"
        with open(csv_filename,'w',newline='') as f:
            writer=csv.writer(f); writer.writerow(["p","q","distance","px","py","pz","qx","qy","qz"])
            for dist,p,q,pos_p,pos_q in sorted(best_pairs):
                writer.writerow([p,q,f"{dist:.10f}",f"{pos_p[0]:.6f}",f"{pos_p[1]:.6f}",f"{pos_p[2]:.6f}",f"{pos_q[0]:.6f}",f"{pos_q[1]:.6f}",f"{pos_q[2]:.6f}"])
        print(f"[Goldbach] CSV saved: {csv_filename}")
    if plot_3d and best_pairs:
        fig=plt.figure(figsize=(12,10)); ax=fig.add_subplot(111,projection='3d')
        ax.set_title(f"Goldbach on Klein Bottle (n={n:,})")
        plot_klein_bottle_mesh(ax, alpha=0.12)
        for _,p,q,pos_p,pos_q in sorted(best_pairs):
            ax.plot([pos_p[0],pos_q[0]],[pos_p[1],pos_q[1]],[pos_p[2],pos_q[2]],'y-',alpha=0.8)
        plt.savefig(f"goldbach_3d_n={n}_topk={top_k}.png",dpi=300)
        plt.show()
    return best_pairs[0][0] if best_pairs else float('inf')

# ────────────────────────────────────────────────
#                  Riemann function
# ────────────────────────────────────────────────

def riemann_champion(T: int, top_k: int = 1000, output_csv: bool = True, plot_3d: bool = True):
    candidates = list(range(14, int(T), max(1, int(T//2000))))
    best_zeros=[]
    pulse_amp=0.18; tilt_amp=0.12; twist_period=math.sqrt(math.log(T if T>2 else 3))
    for t in tqdm(candidates, desc="Riemann", unit="height"):
        s=mpmath.mpc(0.5,t); z=mpmath.zeta(s)
        dev=float(abs(mpmath.re(z)))
        theta=2*math.pi*math.log(t+1)/math.log(T+2)% (2*math.pi)
        phi=2*math.pi*(float(mpmath.re(s))-0.5)/math.log(T+2)% (2*math.pi)
        radial=1+pulse_amp*math.sin(2*math.pi*theta/twist_period); tilt=tilt_amp*math.sin(radial)
        pos=np.array([math.cos(theta),math.sin(theta),math.cos(phi),math.sin(phi)])*radial
        pos[2]+=tilt
        heappush(best_zeros,(dev,float(t),float(mpmath.re(s)),0.0,pos))
        if len(best_zeros)>top_k: heappop(best_zeros)
    if output_csv and best_zeros:
        csv_filename=f"riemann_surface_zeros_T={T}_topk={top_k}.csv"
        with open(csv_filename,'w',newline='') as f:
            writer=csv.writer(f); writer.writerow(["t","Re(s)","deviation","radius"])
            for dev,t,re_s,radius,_ in sorted(best_zeros): writer.writerow([f"{t:.6f}",f"{re_s:.10f}",f"{dev:.2e}",f"{radius:.2e}"])
        print(f"[Riemann] CSV saved: {csv_filename}")
    if plot_3d and best_zeros:
        fig=plt.figure(figsize=(12,10)); ax=fig.add_subplot(111,projection='3d')
        ax.set_title(f"Riemann Zeros on Clifford Torus (T={T:,})")
        xs=[];ys=[];zs=[]
        for _,_,_,_,pos in best_zeros: xs.append(pos[0]); ys.append(pos[1]); zs.append(pos[2])
        ax.scatter(xs,ys,zs,c='lightblue',s=20,alpha=0.6)
        plt.savefig(f"riemann_3d_T={T}_topk={top_k}.png",dpi=300);
        plt.show()
    return max([dev for dev,_,_,_,_ in best_zeros]) if best_zeros else float('inf')

# ────────────────────────────────────────────────
#                  NEW: Twin Prime function
# ────────────────────────────────────────────────

def twinprime_champion(n: int, top_k: int = 1000, output_csv: bool = True, plot_3d: bool = True):
    """Twin Prime version using the same champion surface config"""
    start_time = time.time()
    
    print(f"[TwinPrime] Sieving primes up to {n:,} ...")
    sieve.extend(n)
    primes = list(sieve.primerange(2, n + 1))
    prime_set = set(primes)
    
    loglog_n = math.log(math.log(n + 2))
    pulse_amp = 0.18
    tilt_amp = 0.12
    twist_period = math.sqrt(math.log(n))
    z_shear_amp = 0.08
    geodesic_scale = 0.80
    
    best_twins = []  # (dist, p, p2, pos_p, pos_p2)
    
    print(f"[TwinPrime] Checking candidates...")
    for p in tqdm(primes):
        p2 = p + 2
        if p2 > n or p2 not in prime_set:
            continue
        
        frac_p = math.log(math.log(p + 2)) / loglog_n
        frac_p2 = math.log(math.log(p2 + 2)) / loglog_n
        
        theta_p = 2 * math.pi * frac_p % (2 * math.pi)
        theta_p2 = 2 * math.pi * frac_p2 % (2 * math.pi)
        
        radial = 1 + pulse_amp * math.sin(2 * math.pi * theta_p / twist_period)
        tilt = tilt_amp * math.sin(radial)
        
        pos_p1 = nordstrand_klein(theta_p, 0.5, radial)
        pos_p21 = nordstrand_klein(theta_p2, 0.5, radial)
        pos_p2 = nordstrand_klein(theta_p + math.pi, 0.5, radial)
        pos_p22 = nordstrand_klein(theta_p2 + math.pi, 0.5, radial)
        
        pos_p = (pos_p1 + pos_p2) / 2
        pos_p2 = (pos_p21 + pos_p22) / 2
        
        pos_p[2] += z_shear_amp * math.sin(theta_p) + tilt
        pos_p2[2] += z_shear_amp * math.sin(theta_p2) + tilt
        
        dx = pos_p[0] - pos_p2[0]
        dy = pos_p[1] - pos_p2[1]
        dz = pos_p[2] - pos_p2[2]
        dist = math.sqrt(dx*dx + dy*dy + dz*dz) * geodesic_scale
        
        heappush(best_twins, (dist, p, p2, pos_p, pos_p2))
        if len(best_twins) > top_k:
            heappop(best_twins)
    
    min_dist = best_twins[0][0] if best_twins else float('inf')
    
    # CSV export
    if output_csv and best_twins:
        csv_filename = f"twinprime_surface_pairs_n={n}_topk={top_k}.csv"
        with open(csv_filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["p", "p2", "distance", "pos_p_x", "pos_p_y", "pos_p_z", "pos_p2_x", "pos_p2_y", "pos_p2_z"])
            for d, p, p2, pos_p, pos_p2 in sorted(best_twins):
                writer.writerow([p, p2, f"{d:.10f}", *pos_p, *pos_p2])
        print(f"[TwinPrime] Top {len(best_twins)} pairs saved to: {csv_filename}")
    
    # 3D Visualization with Klein bottle mesh
    if plot_3d and best_twins:
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection='3d')
        ax.set_title(f"Twin Primes on Klein Bottle (n={n:,}, top {top_k})")
        
        plot_klein_bottle_mesh(ax, alpha=0.12)  # ← Surface mesh added
        
        for _, p, p2, pos_p, pos_p2 in sorted(best_twins):
            ax.plot([pos_p[0], pos_p2[0]], [pos_p[1], pos_p2[1]], [pos_p[2], pos_p2[2]],
                    'y-', linewidth=2, alpha=0.8)
            ax.scatter([pos_p[0]], [pos_p[1]], [pos_p[2]], c='blue', s=40)
            ax.scatter([pos_p2[0]], [pos_p2[1]], [pos_p2[2]], c='red', s=40)
        
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        plt.savefig(f"twinprime_3d_n={n}_topk={top_k}.png", dpi=300, bbox_inches='tight')
        plt.show()
        print(f"[TwinPrime] 3D plot + Klein bottle mesh saved: twinprime_3d_n={n}_topk={top_k}.png")
    
    return min_dist

# ────────────────────────────────────────────────
#                  Main CLI
# ────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python combined_surface_tester_with_mesh.py <N> [mode=goldbach|riemann|twinprime] [top_k]")
        sys.exit(1)
    
    N = int(sys.argv[1])
    mode = sys.argv[2].lower() if len(sys.argv) > 2 else "goldbach"
    top_k = int(sys.argv[3]) if len(sys.argv) > 3 else 1000
    
    print(f"\n=== Champion Surface Test @ {mode.upper()} = {N:,} ===\n")
    
    if mode in ("goldbach", "g"):
        goldbach_champion(N, top_k=top_k)
    elif mode in ("riemann", "r"):
        riemann_champion(N, top_k=top_k)
    elif mode in ("twinprime", "t"):
        twinprime_champion(N, top_k=top_k)
    else:
        print(f"Unknown mode: {mode}. Use goldbach, riemann, or twinprime")
        sys.exit(1)