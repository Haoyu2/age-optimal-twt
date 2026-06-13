#!/usr/bin/env python3
r"""Analytical relaxation lower bound on weighted mean AoI per regime.

The convex relaxation drops the SP-disjointness constraint, keeping only the
density bound sum_i d_i/T_i <= 1 and the floors T_i >= max(T_i^min, d_max).
Its optimum lower-bounds the cost of ANY feasible schedule, so the predicted
weighted mean AoI of the water-filled (fractional, unrounded, unpacked)
periods is a valid lower bound. Mirrors the C++ scheduler math exactly.

Writes lb_macros.tex (\ResSkewLB etc.) and prints a per-regime table.
"""

import sys

# Provable lower bound on the in-SP delivery delay: the experiment generates
# each update 2 ms before its SP, so the age at delivery is at least 2 ms.
# Using this (rather than the ~4 ms mean) keeps LB a valid lower bound on the
# measured weighted AoI (LB <= measured in every regime).
DELTA = 2e-3


def sp_success(p, k):
    return 1.0 - (1.0 - p) ** k


def optimal_k(p, c, kmax):
    best_k, best_f = 1, float("inf")
    for k in range(1, kmax + 1):
        f = (k + c) * (1.0 / sp_success(p, k) - 0.5)
        if f < best_f:
            best_f, best_k = f, k
    return best_k


def stations(n, weight_skew, budget_scale, fading, mixed, uniform_budget=0.0):
    out = []
    for i in range(n):
        w = (weight_skew if i % 2 else 1.0) if weight_skew > 0 else 1.0 + (i % 3)
        rho = uniform_budget if uniform_budget > 0 else \
            budget_scale * (0.04 + 0.01 * (i % 4))
        loss = (0.15 + 0.15 * (i % 4)) if fading else 0.0
        p = 1.0 - loss
        if mixed:
            airtime = 300e-6 if i % 2 else 900e-6
            overhead = 500e-6
        else:
            airtime = 1e-3
            overhead = 2e-3
        out.append((w, rho, p, airtime, overhead))
    return out


def relaxation_lb(stas, kmax):
    durations, floors, sqrt_c, age_c, psucc = [], [], [], [], []
    for (w, rho, p, airtime, overhead) in stas:
        k = optimal_k(p, overhead / airtime, kmax)
        d = k * airtime + overhead
        ps = sp_success(p, k)
        a = w * (1.0 / ps - 0.5)
        durations.append(d)
        floors.append(d / rho)
        sqrt_c.append(d / a)
        age_c.append(a)
        psucc.append(ps)
    d_max = max(durations)
    floors = [max(f, d_max) for f in floors]

    def periods(lam):
        return [max(floors[i], (lam * sqrt_c[i]) ** 0.5) for i in range(len(stas))]

    def density(T):
        return sum(durations[i] / T[i] for i in range(len(stas)))

    if density(periods(0.0)) <= 1.0:
        T = periods(0.0)
    else:
        hi = 1.0
        while density(periods(hi)) > 1.0:
            hi *= 2.0
        lo = 0.0
        for _ in range(100):
            mid = (lo + hi) / 2
            if density(periods(mid)) > 1.0:
                lo = mid
            else:
                hi = mid
        T = periods(hi)

    # predicted weighted mean AoI of the (infeasible) relaxation = lower bound
    num = sum(stas[i][0] * (DELTA + T[i] * (1.0 / psucc[i] - 0.5))
              for i in range(len(stas)))
    den = sum(s[0] for s in stas)
    return 1e3 * num / den  # ms


REGIMES = {
    "Loose":      dict(weight_skew=0, budget_scale=1, fading=False, mixed=False),
    "Tight":      dict(weight_skew=0, budget_scale=2, fading=False, mixed=False),
    "Skew":       dict(weight_skew=8, budget_scale=2, fading=False, mixed=False),
    "Fading":     dict(weight_skew=0, budget_scale=2, fading=True,  mixed=False),
    "FadingSkew": dict(weight_skew=8, budget_scale=2, fading=True,  mixed=False),
    "Ubind":      dict(weight_skew=8, budget_scale=0, fading=False, mixed=False,
                       uniform_budget=0.12),
    "Ubindfade":  dict(weight_skew=8, budget_scale=0, fading=True,  mixed=False,
                       uniform_budget=0.12),
}


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    out = sys.argv[2] if len(sys.argv) > 2 else "lb_macros.tex"
    print(f"{'regime':<12}{'LB [ms]':>10}")
    with open(out, "w") as f:
        for name, cfg in REGIMES.items():
            kmax = 1 if cfg["fading"] else 8
            lb = relaxation_lb(stations(n, **cfg), kmax)
            print(f"{name:<12}{lb:>10.2f}")
            f.write(f"\\newcommand{{\\Res{name}LB}}{{{lb:.1f}}}\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
