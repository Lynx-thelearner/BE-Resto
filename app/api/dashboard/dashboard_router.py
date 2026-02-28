from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.auth import require_role
from orm_models import RoleEnum
from app.models.dashboard.dashboard_schema import DashboardSummary
from app.api.dashboard import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_summary(
    db: Session = Depends(get_db),
    current_user=Depends(require_role(RoleEnum.admin, RoleEnum.pegawai)),
):
    """Ambil ringkasan dashboard: order hari ini, pendapatan, meja, menu populer, chart 7 hari."""
    return dashboard_service.get_dashboard_summary(db)
