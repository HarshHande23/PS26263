from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
import math

from app.core.database import get_db
from app.core.deps import get_current_active_user, require_roles
from app.core.enums import UserRole
from app.models.institution import Institution
from app.models.programme import Programme
from app.models.academic_year import AcademicYear
from app.models.approved_intake import ApprovedIntake
from app.models.user import User
from app.schemas.institution import (
    InstitutionCreate, InstitutionUpdate, InstitutionOut, InstitutionSummary,
    PaginatedInstitutions, ProgrammeCreate, ProgrammeOut,
    AcademicYearCreate, AcademicYearOut, ApprovedIntakeCreate, ApprovedIntakeOut,
)

router = APIRouter()


def _check_institution_access(institution_id: UUID, current_user: User) -> None:
    """Raise 403 if college-level user tries to access another institution."""
    if current_user.role in (UserRole.COLLEGE_ADMIN, UserRole.ADMISSION_STAFF):
        if current_user.institution_id != institution_id:
            raise HTTPException(status_code=403, detail="Access denied to this institution")


@router.get("", response_model=PaginatedInstitutions)
def list_institutions(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    state: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    q = db.query(Institution)

    # College users see only their own institution
    if current_user.role in (UserRole.COLLEGE_ADMIN, UserRole.ADMISSION_STAFF, UserRole.STUDENT):
        if current_user.institution_id:
            q = q.filter(Institution.id == current_user.institution_id)
        else:
            return PaginatedInstitutions(items=[], total=0, page=page, size=size, pages=0)

    if search:
        q = q.filter(Institution.name.ilike(f"%{search}%") | Institution.aicte_id.ilike(f"%{search}%"))
    if state:
        q = q.filter(Institution.state.ilike(f"%{state}%"))
    if is_active is not None:
        q = q.filter(Institution.is_active == is_active)

    total = q.count()
    items = q.offset((page - 1) * size).limit(size).all()
    return PaginatedInstitutions(
        items=items, total=total, page=page, size=size, pages=math.ceil(total / size)
    )


@router.get("/{institution_id}", response_model=InstitutionOut)
def get_institution(
    institution_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _check_institution_access(institution_id, current_user)
    inst = db.query(Institution).filter_by(id=institution_id).first()
    if not inst:
        raise HTTPException(status_code=404, detail="Institution not found")
    return inst


@router.post("", response_model=InstitutionOut, status_code=201)
def create_institution(
    payload: InstitutionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.AICTE_ADMIN)),
):
    existing = db.query(Institution).filter_by(aicte_id=payload.aicte_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="AICTE ID already registered")
    inst = Institution(**payload.model_dump())
    db.add(inst)
    db.commit()
    db.refresh(inst)
    return inst


@router.put("/{institution_id}", response_model=InstitutionOut)
def update_institution(
    institution_id: UUID,
    payload: InstitutionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(
        UserRole.SUPER_ADMIN, UserRole.AICTE_ADMIN, UserRole.COLLEGE_ADMIN
    )),
):
    _check_institution_access(institution_id, current_user)
    inst = db.query(Institution).filter_by(id=institution_id).first()
    if not inst:
        raise HTTPException(status_code=404, detail="Institution not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(inst, field, value)
    db.commit()
    db.refresh(inst)
    return inst


# ── Programmes ──────────────────────────────────────────────────────────────

@router.get("/{institution_id}/programmes", response_model=List[ProgrammeOut])
def list_programmes(
    institution_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _check_institution_access(institution_id, current_user)
    return db.query(Programme).filter_by(institution_id=institution_id, is_active=True).all()


@router.post("/{institution_id}/programmes", response_model=ProgrammeOut, status_code=201)
def create_programme(
    institution_id: UUID,
    payload: ProgrammeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(
        UserRole.SUPER_ADMIN, UserRole.AICTE_ADMIN, UserRole.COLLEGE_ADMIN
    )),
):
    _check_institution_access(institution_id, current_user)
    prog = Programme(institution_id=institution_id, **{
        k: v for k, v in payload.model_dump().items() if k != "institution_id"
    })
    db.add(prog)
    db.commit()
    db.refresh(prog)
    return prog


# ── Academic Years ──────────────────────────────────────────────────────────

@router.get("/{institution_id}/academic-years", response_model=List[AcademicYearOut])
def list_academic_years(
    institution_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _check_institution_access(institution_id, current_user)
    return db.query(AcademicYear).filter_by(institution_id=institution_id).all()


@router.post("/{institution_id}/academic-years", response_model=AcademicYearOut, status_code=201)
def create_academic_year(
    institution_id: UUID,
    payload: AcademicYearCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(
        UserRole.SUPER_ADMIN, UserRole.AICTE_ADMIN, UserRole.COLLEGE_ADMIN
    )),
):
    _check_institution_access(institution_id, current_user)
    ay = AcademicYear(institution_id=institution_id, **{
        k: v for k, v in payload.model_dump().items() if k != "institution_id"
    })
    db.add(ay)
    db.commit()
    db.refresh(ay)
    return ay


# ── Approved Intake ─────────────────────────────────────────────────────────

@router.get("/{institution_id}/intake", response_model=List[ApprovedIntakeOut])
def list_intake(
    institution_id: UUID,
    programme_id: Optional[UUID] = None,
    academic_year_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _check_institution_access(institution_id, current_user)
    q = db.query(ApprovedIntake).join(Programme).filter(
        Programme.institution_id == institution_id
    )
    if programme_id:
        q = q.filter(ApprovedIntake.programme_id == programme_id)
    if academic_year_id:
        q = q.filter(ApprovedIntake.academic_year_id == academic_year_id)
    return q.all()


@router.post("/{institution_id}/intake", response_model=ApprovedIntakeOut, status_code=201)
def create_intake(
    institution_id: UUID,
    payload: ApprovedIntakeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(
        UserRole.SUPER_ADMIN, UserRole.AICTE_ADMIN, UserRole.COLLEGE_ADMIN
    )),
):
    _check_institution_access(institution_id, current_user)
    intake = ApprovedIntake(**payload.model_dump())
    db.add(intake)
    db.commit()
    db.refresh(intake)
    return intake
