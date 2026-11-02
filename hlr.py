"""
Half-Life Regression (HLR) — Settles & Meeder, ACL 2016
=========================================================
Core equations
  Forgetting curve  : p  = 2^(−Δ/h)
  Estimated HL      : ĥ  = 2^(Θ·x)
  Algebraic HL      : h  = −Δ / log₂(p)
  Loss              : (p−p̂)² + α(h−ĥ)² + λ‖Θ‖²
  Optimiser         : AdaGrad (Duchi et al., 2011)
"""
import math

# ── Hyperparameters ──────────────────────────────────────────────────────────
LAMBDA = 0.1      # L2 regularisation
ALPHA  = 0.01     # Weight of half-life term in loss
ETA    = 0.001    # AdaGrad base learning rate

# Bounds prevent overflow / underflow (from paper: 15 min → 9 months)
MIN_HL = 1 / 96   # 15 minutes expressed in days
MAX_HL = 274.0    # ~9 months expressed in days


# ── Feature engineering ──────────────────────────────────────────────────────
def feature_vector(n_seen: int, n_correct: int, n_incorrect: int) -> list:
    """
    x = [bias, √n_seen, √n_correct, √n_incorrect]
    Square-root dampening per footnote 5 in the paper.
    """
    return [
        1.0,
        math.sqrt(max(n_seen,      0)),
        math.sqrt(max(n_correct,   0)),
        math.sqrt(max(n_incorrect, 0)),
    ]


# ── Core HLR equations ───────────────────────────────────────────────────────
def estimate_half_life(theta: list, x: list) -> float:
    """ĥ = 2^(Θ·x), clamped to valid range."""
    dot = sum(t * xi for t, xi in zip(theta, x))
    return max(MIN_HL, min(MAX_HL, 2.0 ** dot))


def recall_probability(delta: float, h: float) -> float:
    """p̂ = 2^(−Δ/h).  δ in days, h in days."""
    return 2.0 ** (-delta / max(h, MIN_HL))


def algebraic_half_life(p: float, delta: float) -> float:
    """Invert Ebbinghaus: h = −Δ / log₂(p)."""
    p     = max(0.0001, min(0.9999, p))
    delta = max(delta, 1e-6)
    return min(MAX_HL, max(MIN_HL, -delta / math.log2(p)))


# ── AdaGrad update ───────────────────────────────────────────────────────────
def adagrad_update(
    theta:      list,
    grad_accum: list,
    x:          list,
    p:          float,
    delta:      float,
    h_hat:      float,
    p_hat:      float,
    alpha: float = ALPHA,
    lam:   float = LAMBDA,
    eta:   float = ETA,
):
    """
    One AdaGrad step.  Returns (new_theta, new_grad_accum).

    Gradient derivation (chain rule on the HLR loss):
      ∂ℓ/∂θk = 2(p̂−p)·ln²2·p̂·(Δ/ĥ)·xk          [recall term]
             + 2α(ĥ−h)·ln2·ĥ·xk                    [half-life term]
             + 2λ·θk                                  [regularisation]
    """
    h_alg  = algebraic_half_life(p, delta)
    ln2    = math.log(2)
    new_th = list(theta)
    new_ac = list(grad_accum)

    for k, xk in enumerate(x):
        # Recall-loss gradient
        g_recall = (
            2 * (p_hat - p)
            * (ln2 ** 2)
            * p_hat
            * (delta / max(h_hat, MIN_HL))
            * xk
        )
        # Half-life loss gradient
        g_hl = 2 * alpha * (h_hat - h_alg) * ln2 * h_hat * xk
        # Regularisation gradient
        g_reg = 2 * lam * theta[k]

        grad       = g_recall + g_hl + g_reg
        new_ac[k] += grad ** 2
        denom      = math.sqrt(new_ac[k]) if new_ac[k] > 0 else 1.0
        new_th[k]  = theta[k] - eta * grad / denom

    return new_th, new_ac


# ── Scheduling ───────────────────────────────────────────────────────────────
def days_until_next_review(h_hat: float) -> float:
    """
    Schedule next review at the half-life point,
    i.e. when predicted recall probability = 0.5.
    """
    return h_hat
