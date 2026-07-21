"""
utils/db.py
JSON File Storage Layer (data/database.json)
Provides persistent storage for candidates, scores, statuses, HR approval flags, and assigned interview slots.
"""

import json
import os
import pandas as pd

DB_FILE = "data/database.json"

def init_db():
    """
    Ensures the data directory and data/database.json file exist with initial schema.
    """
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({"candidates": [], "evaluations": []}, f, indent=4)

def load_data():
    """
    Loads JSON dictionary from data/database.json.
    """
    init_db()
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {"candidates": [], "evaluations": []}

def save_data(data):
    """
    Saves JSON dictionary to data/database.json.
    """
    os.makedirs("data", exist_ok=True)
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def save_candidate(candidate_id, name, role, score, status="Pending", approved=False, interview_slot=None):
    """
    Saves or updates a candidate record in data/database.json.
    """
    data = load_data()
    candidates = data.get("candidates", [])
    
    existing = next((c for c in candidates if str(c.get("id")) == str(candidate_id)), None)
    slot_val = interview_slot if interview_slot is not None else (existing.get("interview_slot") if existing else None)
    
    candidate_record = {
        "id": str(candidate_id),
        "name": str(name),
        "role": str(role),
        "score": float(score),
        "status": str(status),
        "approved": bool(approved),
        "interview_slot": slot_val
    }
    
    if existing:
        candidates = [candidate_record if str(c.get("id")) == str(candidate_id) else c for c in candidates]
    else:
        candidates.append(candidate_record)
        
    data["candidates"] = candidates
    save_data(data)

def get_all_candidates():
    """
    Returns list of candidate dictionaries from JSON store.
    """
    data = load_data()
    return data.get("candidates", [])

def get_candidates():
    """
    Returns candidate records as a pandas DataFrame.
    """
    candidates = get_all_candidates()
    if not candidates:
        return pd.DataFrame(columns=["id", "name", "role", "score", "status", "approved", "interview_slot"])
    return pd.DataFrame(candidates)

def update_candidate_status(candidate_id, status, approved, interview_slot=None):
    """
    Updates candidate status, approval flag, and assigned interview slot in data/database.json.
    """
    data = load_data()
    candidates = data.get("candidates", [])
    for c in candidates:
        if str(c.get("id")) == str(candidate_id):
            c["status"] = str(status)
            c["approved"] = bool(approved)
            if interview_slot is not None:
                c["interview_slot"] = str(interview_slot) if interview_slot else None
    data["candidates"] = candidates
    save_data(data)

def get_pending_review_count() -> int:
    """
    Returns count of pending candidates.
    """
    candidates = get_all_candidates()
    return sum(1 for c in candidates if c.get("status") in ["Pending", "Pending Review"])
