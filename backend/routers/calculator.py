import json
import logging
from fastapi import APIRouter, Request
from models.request import CalculatorRequest
from models.response import CalculatorResponse
from services.calculator import lookup_fine
from services.llm import call_llm
from utils.parivahan import build_parivahan_link
from utils.text import clean_json_response
from pathlib import Path

logger = logging.getLogger(__name__)
router = APIRouter()

CALC_PROMPT = Path("prompts/calculator.txt").read_text(encoding="utf-8")


@router.post("", response_model=CalculatorResponse)
async def calculate_fine(req: CalculatorRequest):
    # ── 1. Try structured lookup first (no LLM, no hallucination) ────────────
    result = lookup_fine(
        violation=req.violation,
        vehicle_type=req.vehicle_type,
        state=req.state,
        offense_count=req.offense_count,
    )

    if result:
        return CalculatorResponse(
            violation=req.violation,
            section=result["section"],
            vehicle_type=req.vehicle_type,
            state=req.state,
            offense=req.offense_count,
            fine_min=result["fine_min"],
            fine_max=result["fine_max"],
            fine_display=f"₹{result['fine_min']:,} – ₹{result['fine_max']:,}",
            state_note=result.get("state_note"),
            parivahan_link=build_parivahan_link(req.state),
        )

    # ── 2. Fall back to LLM for unknown violations ────────────────────────────
    prompt = CALC_PROMPT.format(
        violation=req.violation,
        vehicle_type=req.vehicle_type,
        state=req.state,
        offense_count=req.offense_count,
    )

    try:
        raw = await call_llm(
            [{"role": "user", "content": prompt}],
            system="You are a traffic fine calculator. Return ONLY valid JSON. No prose.",
        )
        clean = clean_json_response(raw)
        data = json.loads(clean)
    except Exception as e:
        logger.error(f"Calculator LLM failed: {e}")
        return CalculatorResponse(
            violation=req.violation,
            section="Section 177, MV Act 1988",
            vehicle_type=req.vehicle_type,
            state=req.state,
            offense=req.offense_count,
            fine_min=500,
            fine_max=1500,
            fine_display="₹500 – ₹1,500",
            state_note="Could not determine exact fine. Please check echallan.parivahan.gov.in",
            parivahan_link=build_parivahan_link(req.state),
        )

    return CalculatorResponse(
        violation=req.violation,
        section=data.get("section", "Section 177, MV Act 1988"),
        vehicle_type=req.vehicle_type,
        state=req.state,
        offense=req.offense_count,
        fine_min=int(data.get("fine_min", 500)),
        fine_max=int(data.get("fine_max", 1500)),
        fine_display=f"₹{int(data.get('fine_min', 500)):,} – ₹{int(data.get('fine_max', 1500)):,}",
        state_note=data.get("state_note"),
        parivahan_link=build_parivahan_link(req.state),
    )
