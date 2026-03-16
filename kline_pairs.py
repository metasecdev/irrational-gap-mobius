import math
from sympy import primerange, isprime
from heapq import heappush, heappop

def nordstrand_klein(theta, phi, scale=1.0):
    c = math.cos(theta)
    s = math.sin(theta)
    c2 = math.cos(phi / 2)
    s2 = math.sin(phi / 2)
    x = (2 + c2 * s - s2 * math.sin(2*theta)) * c * scale
    y = (2 + c2 * s - s2 * math.sin(2*theta)) * s * scale
    z = s2 * s + c2 * math.sin(2*theta) * scale
    return (x, y, z)

def champion_distance(n, max_candidates=50000, verbose=True):
    if n % 2 != 0 or n < 4:
        return None
    
    primes = list(primerange(2, n+1))
    loglog_n = math.log(math.log(n + 2))
    
    pulse_amp = 0.18
    tilt_amp  = 0.12
    twist_period = math.sqrt(math.log(n))
    z_shear = 0.08
    
    best_pairs = []  # min-heap (dist, p, q)
    
    max_p_check = n // 10
    
    count_checked = 0
    for p in primes:
        if p > max_p_check:
            break
        q = n - p
        if q not in primes:
            continue
        
        count_checked += 1
        
        frac_p = math.log(math.log(p + 2)) / loglog_n
        frac_q = math.log(math.log(q + 2)) / loglog_n
        
        theta_p = 2 * math.pi * frac_p % (2 * math.pi)
        theta_q = 2 * math.pi * frac_q % (2 * math.pi)
        
        radial = 1 + pulse_amp * math.sin(2 * math.pi * theta_p / twist_period)
        tilt = tilt_amp * math.sin(radial)
        
        pos_p = nordstrand_klein(theta_p, 0.5, radial)
        pos_q = nordstrand_klein(theta_q, 0.5, radial)
        
        pos_p = (pos_p[0], pos_p[1], pos_p[2] + z_shear * math.sin(theta_p) + tilt)
        pos_q = (pos_q[0], pos_q[1], pos_q[2] + z_shear * math.sin(theta_q) + tilt)
        
        dx = pos_p[0] - pos_q[0]
        dy = pos_p[1] - pos_q[1]
        dz = pos_p[2] - pos_q[2]
        dist = math.sqrt(dx*dx + dy*dy + dz*dz) * 0.80
        
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