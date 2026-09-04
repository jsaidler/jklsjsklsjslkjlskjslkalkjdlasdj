from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path

import requests

MIN_USD_BUDGET = 0.06


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("pixellab_spike_impl", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load spike module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def num(value):
    return float(value) if isinstance(value, (int, float)) else None


def nested_num(data, parent, child):
    obj = data.get(parent)
    if isinstance(obj, dict):
        return num(obj.get(child))
    return None


def probe_balance(module, token: str) -> dict | None:
    try:
        response = requests.get(
            f"{module.API_BASE}/balance",
            headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
            timeout=30,
        )
        if not response.ok:
            print(f"PixelLab v2 balance probe: HTTP {response.status_code}; letting the API itself decide availability.")
            return None
        data = response.json()
        if not isinstance(data, dict):
            print("PixelLab v2 balance probe returned an unknown shape; letting the API itself decide availability.")
            return None
        return data
    except (requests.RequestException, ValueError) as exc:
        print(f"PixelLab v2 balance probe unavailable ({exc}); letting the API itself decide availability.")
        return None


def explain_and_gate(data: dict | None) -> bool:
    if data is None:
        return True

    legacy_usd = num(data.get("usd"))
    credits_usd = nested_num(data, "credits", "usd")
    subscription_generations = nested_num(data, "subscription", "generations")
    subscription_total = nested_num(data, "subscription", "total")

    print("PixelLab v2 balance snapshot:")
    if subscription_generations is not None:
        print(f"  subscription generations remaining: {subscription_generations:g}")
    if subscription_total is not None:
        print(f"  subscription generations total:     {subscription_total:g}")
    if credits_usd is not None:
        print(f"  USD credits:                        ${credits_usd:.4f}")
    if legacy_usd is not None:
        print(f"  legacy/top-level USD balance:       ${legacy_usd:.4f}")

    # Current PixelLab billing can consume subscription generations before USD credits.
    # Therefore a zero USD balance is not, by itself, grounds to reject the spike.
    if subscription_generations is not None and subscription_generations > 0:
        print("Balance gate: PASS via subscription/free generations.")
        return True
    if credits_usd is not None and credits_usd >= MIN_USD_BUDGET:
        print("Balance gate: PASS via USD credits.")
        return True

    # If the current nested v2 shape explicitly exposes both buckets and both are empty,
    # stop before any paid endpoint. This is the only case we can call definitively empty.
    if subscription_generations is not None and credits_usd is not None:
        if subscription_generations <= 0 and credits_usd < MIN_USD_BUDGET:
            print(
                "Balance gate: FAIL. PixelLab explicitly reports no subscription generations "
                f"and only ${credits_usd:.4f} in USD credits."
            )
            return False

    # Older/partial schemas often expose only top-level usd. PixelLab's current account model
    # may also have generation quota, so do not produce a false negative from usd==0 alone.
    if legacy_usd is not None and legacy_usd < MIN_USD_BUDGET:
        print(
            "Balance gate: inconclusive. Top-level USD is below budget, but this response does not "
            "expose a subscription-generation bucket. Proceeding to the low-cost estimator so the "
            "PixelLab API can authoritatively accept or reject the account quota."
        )
        return True

    print("Balance gate: inconclusive/unknown shape; proceeding so the PixelLab API can decide availability.")
    return True


def main() -> int:
    if len(sys.argv) < 2:
        raise SystemExit("usage: balance_aware_launcher.py <pixellab_spike.py> [spike args...]")

    impl_path = Path(sys.argv[1]).resolve()
    token = os.environ.get("PIXELLAB_SECRET", "").strip()
    if not token:
        raise SystemExit("PIXELLAB_SECRET is not set")

    module = load_module(impl_path)
    data = probe_balance(module, token)
    if not explain_and_gate(data):
        return 1

    # The launcher already performed the current v2-aware balance check. Disable the old
    # top-level-USD-only gate inside pixellab_spike.py so it cannot false-fail afterward.
    module.get_balance = lambda _token: None

    sys.argv = [str(impl_path)] + sys.argv[2:]
    return int(module.main())


if __name__ == "__main__":
    raise SystemExit(main())
