from fastapi import APIRouter
from app.api.v1 import auth, institutions, students, uploads, findings, alerts, dashboard, verification, reports

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(institutions.router, prefix="/institutions", tags=["Institutions"])
api_router.include_router(students.router, prefix="/students", tags=["Students"])
api_router.include_router(uploads.router, prefix="/uploads", tags=["Bulk Import"])
api_router.include_router(findings.router, prefix="/findings", tags=["Validation Findings"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(verification.router, prefix="/verification", tags=["Verification"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports & Compliance"])
