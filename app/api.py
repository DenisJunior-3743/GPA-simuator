from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional

from .gpa_calculator import compute_gpa
from .cgpa_calculator import update_cgpa, required_gpa_for_target
from .simulator import generate_grade_combinations, find_minimal_gpa_for_target
from . import vault_manager as vault

app = FastAPI(title='GPA & CGPA Simulator (Offline API)')

# Development CORS: allow browser / web builds running on localhost to call the API.
# This is permissive on purpose for local testing only. If you expose the API,
# restrict origins appropriately.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class CourseItem(BaseModel):
    # limit credit units to 1..5 to match backend validation
    credit_units: int = Field(..., ge=1, le=5)
    grade: str

class GPACalcRequest(BaseModel):
    # require at least one course
    courses: List[CourseItem] = Field(..., min_items=1)

class CGPAUpdateRequest(BaseModel):
    old_cgpa: float
    old_total_cu: int
    new_gpa: float
    new_cu: int

class RequiredGPARequest(BaseModel):
    old_cgpa: float
    old_total_cu: int
    new_cu: int
    target_cgpa: float

class SimulateRequest(BaseModel):
    cus: List[int]
    target_gpa: float
    tolerance_low: Optional[float] = 0.0
    tolerance_high: Optional[float] = 0.4
    max_results: Optional[int] = 30
    allowed_letters: Optional[List[str]] = None
    allow_A_if_needed: Optional[bool] = True

@app.post('/gpa/calculate')
def api_calculate_gpa(req: GPACalcRequest):
    courses = [(c.credit_units, c.grade) for c in req.courses]
    try:
        gpa = compute_gpa(courses)
        return {'gpa': gpa}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post('/cgpa/update')
def api_update_cgpa(req: CGPAUpdateRequest):
    try:
        new = update_cgpa(req.old_cgpa, req.old_total_cu, req.new_gpa, req.new_cu)
        return {'new_cgpa': new}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post('/cgpa/required')
def api_required_gpa(req: RequiredGPARequest):
    try:
        required = required_gpa_for_target(req.old_cgpa, req.old_total_cu, req.new_cu, req.target_cgpa)
        return {'required_gpa': required}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post('/simulate/grades')
def api_simulate(req: SimulateRequest):
    try:
        num = len(req.cus)
        results = generate_grade_combinations(num, req.cus, req.target_gpa, req.tolerance_low, req.tolerance_high, req.max_results, req.allowed_letters, req.allow_A_if_needed)
        return {'results': [{'grades': list(r[0]), 'gpa': r[1]} for r in results]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post('/vault/init')
def api_vault_init():
    vault.init_db()
    return {'status': 'initialized'}

@app.post('/vault/create_user')
def api_create_user(name: str, program: Optional[str] = None, duration: Optional[int] = None):
    uid = vault.create_user(name, program, duration)
    return {'user_id': uid}

@app.get('/vault/users/{user_id}/semesters')
def api_get_semesters(user_id: int):
    sems = vault.get_semesters_for_user(user_id)
    return {'semesters': sems}
