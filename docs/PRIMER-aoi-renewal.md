# Primer: The TWT Age-of-Information Formula (Proposition 1)

A self-contained derivation of the paper's central single-station result:

$$
\bar A \;=\; \delta + T\!\left(\frac{1}{p} - \frac{1}{2}\right),
\qquad
\bar A^{\mathrm{peak}} \;=\; \delta + \frac{T}{p}.
$$

Here $T$ is the TWT wake interval (the service-period period), $p$ is the
probability that a service period (SP) succeeds, and $\delta$ is the mean
in-SP delivery delay. Everything below builds these two lines from scratch.

---

## 1. What is Age of Information?

For a source that sends timestamped updates to a monitor, the **Age of
Information** at time $t$ is

$$
A(t) = t - g(t),
$$

where $g(t)$ is the generation time of the **freshest update the monitor has
received so far**. Two things happen to $A(t)$ over time:

- **It grows at unit rate.** With no new delivery, every second that passes
  makes the freshest-known information one second older: $\frac{d}{dt}A(t)=1$.
- **It drops on delivery.** When a fresher update arrives, $g(t)$ jumps
  forward, so $A(t)$ falls.

The result is a **sawtooth**: linear ramps up, sudden drops down. We care
about its long-run **time-average** $\bar A$ (overall freshness) and its
average **peak** $\bar A^{\mathrm{peak}}$ (worst-case staleness per cycle).

```
A(t)
  |        peak = delta + X
  |        /|            /|
  |       / |           / |
  |      /  |          /  |
  |     /   |         /   |
  |   _/    |       _/    |        <- resets to delta on each successful delivery
  | delta   |     delta   |
  +----+----+-----+-------+----> t
       ^          ^
    delivery   delivery
```

---

## 2. The TWT system, reduced to its essentials

A station governed by a TWT agreement behaves like this:

1. **It wakes every $T$ seconds** (the wake interval) for a short service
   period, and sleeps in between.
2. **Generate-at-will:** at the start of each SP it samples its source, so
   the update it tries to send is *fresh* (age $\approx 0$) when the SP
   begins.
3. **Per-SP block fading:** the channel coherence time exceeds the SP, so
   *all* transmission attempts inside one SP succeed or fail together. Model
   each SP as an independent Bernoulli trial: it **succeeds with probability
   $p$**, independently across SPs.
4. **On a successful SP**, the fresh sample reaches the AP after a small
   in-SP delay $\delta$ (contention + airtime). So at the delivery instant
   the age resets to $\delta$ — not to $0$, because the update spent $\delta$
   in flight.
5. **On a failed SP**, nothing is delivered; the age keeps climbing. The next
   SP's fresh sample is what eventually gets through.

> **Why "per-SP success $p$" is the right primitive.** If you instead model
> per-*attempt* i.i.d. loss with $k$ retries per SP, the per-SP success is
> $1-(1-q)^k$, which rushes to $1$ as $k$ grows and the problem trivializes.
> The interesting regime — where freshness genuinely depends on the schedule
> — is block fading, where one $p$ summarizes the whole SP. See the companion
> note on the $k^\*$ batching lemma.

---

## 3. The renewal structure

Look only at the **successful** deliveries. They reset the age and partition
time into **cycles**: a cycle runs from one successful delivery to the next.

Because each SP independently succeeds with probability $p$, the number of
SPs from just after one success up to and including the next success is a
**geometric** random variable:

$$
M \in \{1,2,3,\dots\}, \qquad \Pr[M=m] = (1-p)^{m-1}\,p.
$$

(You wait through $m-1$ failures, then one success.) Its first two moments —
which are all we need — are

$$
\mathbb{E}[M] = \frac{1}{p}, \qquad
\operatorname{Var}(M) = \frac{1-p}{p^2}, \qquad
\mathbb{E}[M^2] = \operatorname{Var}(M) + \mathbb{E}[M]^2 = \frac{2-p}{p^2}.
$$

Each cycle spans exactly $M$ service periods, so its **length** is

$$
X = M\,T, \qquad
\mathbb{E}[X] = \frac{T}{p}, \qquad
\mathbb{E}[X^2] = T^2\,\mathbb{E}[M^2] = \frac{(2-p)\,T^2}{p^2}.
$$

Successive cycles are i.i.d., so $\{A(t)\}$ is a **renewal-reward process**:
the perfect setting for computing a time-average.

---

## 4. The renewal-reward theorem

For a process that repeats over i.i.d. cycles, the long-run time-average
equals the **expected area under one cycle** divided by the **expected cycle
length**:

$$
\bar A = \frac{\mathbb{E}[Q]}{\mathbb{E}[X]},
\qquad
Q = \int_{\text{one cycle}} A(t)\,dt .
$$

So we only need the area $Q$ of one sawtooth tooth.

### The area of one tooth

Inside a cycle of length $X$:

- just after the delivery that opens it, the age is $\delta$;
- it then ramps up at unit rate for the whole cycle, reaching $\delta + X$
  just before the next delivery.

That shape is a **trapezoid** = rectangle (height $\delta$, width $X$) plus
triangle (base $X$, height $X$):

$$
Q = \underbrace{\delta\,X}_{\text{rectangle}}
  + \underbrace{\tfrac12 X^2}_{\text{triangle}} .
$$

### Putting it together

$$
\bar A = \frac{\mathbb{E}[\delta X + \tfrac12 X^2]}{\mathbb{E}[X]}
       = \delta + \frac{\mathbb{E}[X^2]}{2\,\mathbb{E}[X]} .
$$

Substitute the geometric moments:

$$
\frac{\mathbb{E}[X^2]}{2\,\mathbb{E}[X]}
= \frac{(2-p)T^2/p^2}{2\,(T/p)}
= \frac{(2-p)\,T}{2p}
= T\!\left(\frac{1}{p} - \frac{1}{2}\right).
$$

Therefore

$$
\boxed{\;\bar A = \delta + T\!\left(\dfrac{1}{p} - \dfrac{1}{2}\right).\;}
$$

---

## 5. Peak AoI

The peak of each tooth is the age **just before** a delivery, namely
$\delta + X$. Averaging over cycles:

$$
\bar A^{\mathrm{peak}} = \mathbb{E}[\delta + X] = \delta + \mathbb{E}[X]
= \boxed{\;\delta + \dfrac{T}{p}.\;}
$$

Note both formulas are **linear in $T$** with channel-dependent slopes
($\tfrac1p-\tfrac12$ for mean, $\tfrac1p$ for peak). That linearity is the
hinge the whole multi-station theory swings on (Section 7).

---

## 6. Sanity checks

| Limit | Mean $\bar A$ | Reading |
|---|---|---|
| $p=1$ (perfect channel) | $\delta + T/2$ | classic periodic-sampling age: a sawtooth that resets every $T$ averages half its height |
| $p\to 0$ (dead channel) | $\delta + T/p \to \infty$ | deliveries vanish, information goes stale without bound |
| $p=1$, peak | $\delta + T$ | the age right before each (always-successful) delivery is exactly one period old plus the delay |
| large $T$ | grows like $T/p$ | sleeping longer linearly worsens freshness |

The $p=1$ case recovering $\delta + T/2$ is the load-bearing check: it is the
textbook age of a clean periodic sampler, and our formula must reduce to it
when nothing is ever lost.

These formulas were validated against packet-level ns-3 simulation:
**0.003%** error at $p=1$ and **<1%** mean error under block fading across
$p\in\{0.8,0.6,0.4\}$, with the renewal components $\mathbb{E}[X]$ and
$\mathbb{E}[X^2]/2\mathbb{E}[X]$ each within $1\%$ of $T/p$ and
$T(1/p-1/2)$.

---

## 7. Why this is the keystone of the paper

**(a) It linearizes the scheduling objective.** Summing weighted ages over
$N$ stations,

$$
\sum_i w_i \bar A_i
= \underbrace{\sum_i w_i \delta_i}_{\text{constant }C}
+ \sum_i \underbrace{w_i\!\left(\tfrac{1}{p_i}-\tfrac12\right)}_{\displaystyle a_i}\, T_i .
$$

Minimizing weighted AoI is therefore **minimizing $\sum_i a_i T_i$** — a
*linear* function of the periods $\{T_i\}$. Every later result (the convex
relaxation, water-filling, harmonic rounding, the $5.77$/$8.66$
approximation) rests on this linearity.

**(b) It defines the per-station "importance" weight.** The coefficient

$$
a_i = w_i\!\left(\frac{1}{p_i} - \frac12\right)
$$

is exactly how much station $i$'s period costs the objective. The scheduler's
square-root law assigns $T_i \propto \sqrt{d_i / a_i}$, so stations with high
$a_i$ — high AoI weight $w_i$ **or** poor channel (small $p_i$, large
$1/p_i$) — get **shorter** periods. The $1/p_i$ term is precisely what makes
the scheduler **channel-aware**: a lossy station must wake more often to stay
fresh.

**(c) Peak AoI comes for free.** Because $\bar A^{\mathrm{peak}}$ is also
linear in $T$ (coefficient $w_i/p_i$), every theorem transfers verbatim to
the weighted-peak objective — no separate analysis needed.

---

## 8. Assumptions, stated plainly

The derivation is exact under:

- **Generate-at-will at SP start** — the sample is fresh when the SP begins
  (no stale queueing). Random arrivals would couple stations through a queue
  and turn this into an MDP; that is future work.
- **Per-SP block fading** — i.i.d. Bernoulli($p$) success per SP, coherence
  $\ge$ SP duration. This is what lets one number $p$ summarize an SP.
- **Small, roughly constant in-SP delay $\delta$** — the additive offset; in
  the experiments $\delta$ is a few milliseconds against periods of tens of
  milliseconds.
- **Uplink, one source per station** — single sawtooth per station.

Under these, Proposition 1 is not an approximation but an identity, which is
why simulation matches it to fractions of a percent.

---

### One-paragraph recap

Successful SPs are a renewal process with geometric gaps ($\mathbb{E}[M]=1/p$,
$\mathbb{E}[M^2]=(2-p)/p^2$). Each renewal cycle contributes a trapezoidal
age area $Q=\delta X+\tfrac12X^2$ with $X=MT$. Renewal-reward gives
$\bar A=\delta+\mathbb{E}[X^2]/2\mathbb{E}[X]=\delta+T(1/p-1/2)$, and the
per-cycle peak $\delta+X$ averages to $\delta+T/p$. Both are linear in $T$,
which is exactly why AoI-optimal TWT scheduling reduces to a clean weighted
linear program over the wake intervals.
