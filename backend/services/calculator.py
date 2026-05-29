"""
Structured fine calculator service.

Provides hardcoded fine ranges from MV Act 2019 so the LLM is only
called for nuanced state-specific notes, not for core amounts.
This dramatically reduces hallucination risk.
"""

from typing import Optional

# ---------------------------------------------------------------------------
# Fine schedule – Motor Vehicles (Amendment) Act 2019
# Structure: { violation: { vehicle_type: { offense: (min, max, section) } } }
# ---------------------------------------------------------------------------
FINE_SCHEDULE: dict = {
    "speeding": {
        "LMV": {
            "first":  (1000, 2000, "Section 183, MV Act 1988"),
            "repeat": (2000, 4000, "Section 183, MV Act 1988"),
        },
        "HMV": {
            "first":  (2000, 4000, "Section 183, MV Act 1988"),
            "repeat": (4000, 8000, "Section 183, MV Act 1988"),
        },
        "two_wheeler": {
            "first":  (1000, 2000, "Section 183, MV Act 1988"),
            "repeat": (2000, 4000, "Section 183, MV Act 1988"),
        },
        "three_wheeler": {
            "first":  (1000, 2000, "Section 183, MV Act 1988"),
            "repeat": (2000, 4000, "Section 183, MV Act 1988"),
        },
    },
    "helmet": {
        "two_wheeler": {
            "first":  (1000, 1000, "Section 129, MV Act 1988"),
            "repeat": (1000, 1000, "Section 129, MV Act 1988"),
        },
    },
    "drunk_driving": {
        "LMV": {
            "first":  (10000, 10000, "Section 185, MV Act 1988"),
            "repeat": (15000, 15000, "Section 185, MV Act 1988"),
        },
        "HMV": {
            "first":  (10000, 10000, "Section 185, MV Act 1988"),
            "repeat": (15000, 15000, "Section 185, MV Act 1988"),
        },
        "two_wheeler": {
            "first":  (10000, 10000, "Section 185, MV Act 1988"),
            "repeat": (15000, 15000, "Section 185, MV Act 1988"),
        },
        "three_wheeler": {
            "first":  (10000, 10000, "Section 185, MV Act 1988"),
            "repeat": (15000, 15000, "Section 185, MV Act 1988"),
        },
    },
    "no_license": {
        "_default": {
            "first":  (5000, 5000, "Section 3/181, MV Act 1988"),
            "repeat": (5000, 5000, "Section 3/181, MV Act 1988"),
        },
    },
    "no_insurance": {
        "_default": {
            "first":  (2000, 2000, "Section 196, MV Act 1988"),
            "repeat": (4000, 4000, "Section 196, MV Act 1988"),
        },
    },
    "no_puc": {
        "_default": {
            "first":  (10000, 10000, "Section 190(2), MV Act 1988"),
            "repeat": (10000, 10000, "Section 190(2), MV Act 1988"),
        },
    },
    "seatbelt": {
        "_default": {
            "first":  (1000, 1000, "Section 194B, MV Act 1988"),
            "repeat": (1000, 1000, "Section 194B, MV Act 1988"),
        },
    },
    "mobile_phone": {
        "_default": {
            "first":  (5000, 5000, "Section 184, MV Act 1988"),
            "repeat": (10000, 10000, "Section 184, MV Act 1988"),
        },
    },
    "red_light": {
        "_default": {
            "first":  (1000, 5000, "Section 119/177, MV Act 1988"),
            "repeat": (2000, 10000, "Section 119/177, MV Act 1988"),
        },
    },
    "wrong_side": {
        "_default": {
            "first":  (1000, 5000, "Section 184, MV Act 1988"),
            "repeat": (2000, 10000, "Section 184, MV Act 1988"),
        },
    },
    "triple_riding": {
        "two_wheeler": {
            "first":  (1000, 2000, "Section 128, MV Act 1988"),
            "repeat": (2000, 4000, "Section 128, MV Act 1988"),
        },
    },
    "juvenile_driving": {
        "_default": {
            "first":  (25000, 25000, "Section 199A, MV Act 1988"),
            "repeat": (25000, 25000, "Section 199A, MV Act 1988"),
        },
    },
}

# State-level amendments (reduced fines for some states)
STATE_OVERRIDES: dict = {
    "Gujarat": {
        "speeding": {"fine_note": "Gujarat follows central MV Act rates."},
    },
    "Delhi": {
        "no_puc": {"fine_note": "Delhi enforces strict PUC checks; repeat offenders may face court summons."},
        "drunk_driving": {"fine_note": "Delhi uses Breath Analyser test. DL suspended for 6 months on first offense."},
    },
    "Tamil Nadu": {
        "helmet": {"fine_note": "Tamil Nadu: ₹1,000 fine. No DL suspension for first offense."},
    },
    "Maharashtra": {
        "drunk_driving": {"fine_note": "Maharashtra: Fine ₹10,000 + 6 months imprisonment possible on first offense."},
    },
    "Kerala": {
        "speeding": {"fine_note": "Kerala enforces strict speed limits on NH66 and state highways."},
    },
    "Karnataka": {
        "mobile_phone": {"fine_note": "Karnataka: ₹5,000 fine and licence can be suspended."},
    },
}


def lookup_fine(
    violation: str,
    vehicle_type: str,
    state: str,
    offense_count: str,
) -> Optional[dict]:
    """
    Look up fine from the schedule. Returns dict or None if not found.
    """
    viol_data = FINE_SCHEDULE.get(violation)
    if not viol_data:
        return None

    # Try exact vehicle type, then fall back to _default
    vtype_data = viol_data.get(vehicle_type) or viol_data.get("_default")
    if not vtype_data:
        # For helmet/triple_riding, only two_wheelers — default to that
        vtype_data = next(iter(viol_data.values()), None)
    if not vtype_data:
        return None

    offense_data = vtype_data.get(offense_count) or vtype_data.get("first")
    if not offense_data:
        return None

    fine_min, fine_max, section = offense_data

    # Apply state override note
    state_note = None
    state_ov = STATE_OVERRIDES.get(state, {}).get(violation, {})
    if state_ov:
        state_note = state_ov.get("fine_note")
        fine_min = state_ov.get("fine_min", fine_min)
        fine_max = state_ov.get("fine_max", fine_max)

    return {
        "section": section,
        "fine_min": fine_min,
        "fine_max": fine_max,
        "state_note": state_note,
    }
