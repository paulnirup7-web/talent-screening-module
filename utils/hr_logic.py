"""
hr_logic.py
Root Wrapper Module for HR Business Rules & Dual-Gate Security Logic
Exposes SCREENING_GATE_THRESHOLD, DEFAULT_ROLE_THRESHOLD, GOOD_MATCH_THRESHOLD,
satisfies_dual_gate, can_pass_screening_gate, get_candidate_status, approve_candidate_session,
and run_reverse_screening.
"""

from utils.hr_logic import (
    SCREENING_GATE_THRESHOLD,
    DEFAULT_ROLE_THRESHOLD,
    GOOD_MATCH_THRESHOLD,
    satisfies_dual_gate,
    can_pass_screening_gate,
    get_candidate_status,
    verify_exam_access,
    approve_candidate_session,
    run_reverse_screening
)

__all__ = [
    "SCREENING_GATE_THRESHOLD",
    "DEFAULT_ROLE_THRESHOLD",
    "GOOD_MATCH_THRESHOLD",
    "satisfies_dual_gate",
    "can_pass_screening_gate",
    "get_candidate_status",
    "verify_exam_access",
    "approve_candidate_session",
    "run_reverse_screening"
]
