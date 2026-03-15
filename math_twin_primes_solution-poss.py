import math
from sympy import primerange, isprime
from heapq import heappush, heappop

def nordstrand_klein(theta, phi, scale=1.0):
    """Nordstrand figure-8 Klein bottle immersion (x,y,z)"""
    c = math.cos(theta)
    s = math.sin(theta)
    c2 = math.cos(phi / 2)
    s2 = math.sin(phi / 2)
    c4 = math.cos(phi)
    s4 = math.sin(phi)
    
    x = (2 + c2 * s - s2 * math.sin(2*theta)) * c * scale
    y = (2 + c2 * s - s2 * math.sin(2*theta)) * s * scale
    z = s2 * s + c2 * math.sin(2*theta) * scale
    return (x, y, z)

def champion_distance(n, max_candidates=50000, verbose=True):
    if n % 2 != 0 or n < 4:
        return None
    
    # Step 1: Get primes (use segmented sieve or precomputed for large n)
    print(f"Sieving primes up to {n}...")
    primes = list(primerange(2, n+1))
    print(f"Found {len(primes)} primes")
    
    loglog_n = math.log(math.log(n + 2))
    
    pulse_amp = 0.18
    tilt_amp  = 0.12
    twist_period = math.sqrt(math.log(n))
    z_shear = 0.08
    
    # Priority queue: (dist, p, q)
    best_pairs = []  # min-heap
    
    # Only check small p (up to some fraction) to make it feasible
    max_p_check = n // 10  # adjustable
    
    count_checked = 0
    for p in primes:
        if p > max_p_check:
            break
        q = n - p
        if q not in primes:  # fast set lookup if you convert primes to set
            continue
        
        count_checked += 1
        
        frac_p = math.log(math.log(p + 2)) / loglog_n
        frac_q = math.log(math.log(q + 2)) / loglog_n
        
        theta_p = 2 * math.pi * frac_p % (2 * math.pi)
        theta_q = 2 * math.pi * frac_q % (2 * math.pi)
        
        radial = 1 + pulse_amp * math.sin(2 * math.pi * theta_p / twist_period)
        tilt = tilt_amp * math.sin(radial)  # synchronized
        
        pos_p = nordstrand_klein(theta_p, 0.5, radial)
        pos_q = nordstrand_klein(theta_q, 0.5, radial)
        
        # z-shear + tilt
        pos_p = (pos_p[0], pos_p[1], pos_p[2] + z_shear * math.sin(theta_p) + tilt)
        pos_q = (pos_q[0], pos_q[1], pos_q[2] + z_shear * math.sin(theta_q) + tilt)
        
        # Euclidean distance + approximate geodesic correction (~20% shorter)
        dx = pos_p[0] - pos_q[0]
        dy = pos_p[1] - pos_q[1]
        dz = pos_p[2] - pos_q[2]
        dist = math.sqrt(dx*dx + dy*dy + dz*dz) * 0.80  # geodesic approx
        
        # Keep top candidates
        heappush(best_pairs, (dist, p, q))
        if len(best_pairs) > 1000:
            heappop(best_pairs)
    
    if verbose:
        print(f"Checked {count_checked} candidates")
        print("Top 5 closest pairs:")
        for d, p, q in sorted(best_pairs)[:5]:
            print(f"{p:8d} + {q:8d}   dist ≈ {d:.10f}")
    
    min_dist = best_pairs[0][0] if best_pairs else float('inf')
    return min_dist, len(best_pairs)

# Example run
if __name__ == "__main__":
    n = 10000000  # 10M — change to 100000000 if you have time & RAM
    min_d, num_close = champion_distance(n)
    print(f"\nMinimal surface distance at n={n}: {min_d:.10f}")