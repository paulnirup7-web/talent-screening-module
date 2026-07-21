"""
hr_logic.py
Root Wrapper Module for HR Business Rules & Dual-Gate Security Logic
Exposes SCREENING_GATE_THRESHOLD, DEFAULT_ROLE_THRESHOLD, GOOD_MATCH_THRESHOLD,
satisfies_dual_gate, can_pass_screening_gate, get_candidate_status, approve_candidate_session,
and run_reverse_screening.
"""

SCREENING_GATE_THRESHOLD = 70.0
DEFAULT_ROLE_THRESHOLD = 60.0
GOOD_MATCH_THRESHOLD = 75.0

def satisfies_dual_gate(score, role_threshold=DEFAULT_ROLE_THRESHOLD):
    return score >= SCREENING_GATE_THRESHOLD and score >= role_threshold

def can_pass_screening_gate(score):
    return score >= SCREENING_GATE_THRESHOLD

def get_candidate_status(score):
    if score >= GOOD_MATCH_THRESHOLD:
        return "Strong Match"
    elif score >= SCREENING_GATE_THRESHOLD:
        return "Qualified"
    return "Needs Review"

def verify_exam_access(candidate_id):
    # Logic to verify access
    return True

def approve_candidate_session(candidate_id):
    # Logic to approve session
    return True

def run_reverse_screening(candidate_data):
    # Logic for reverse screening
    return {}

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
