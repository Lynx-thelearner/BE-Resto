from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from decimal import Decimal
from datetime import datetime, timezone, timedelta

from orm_models import Orders, OrderItem, OrderStatusEnum, Meja, Menu, Payment
from app.models.dashboard.dashboard_schema import (
    DashboardSummary, OrderStatusCount, MenuPopuler, PendapatanPerHari
)


def get_dashboard_summary(db: Session) -> DashboardSummary:
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # ===== Order hari ini =====
    orders_today = db.query(Orders).filter(Orders.created_at >= today_start).all()

    total_order_hari_ini = len(orders_today)
    total_selesai = sum(1 for o in orders_today if o.status == OrderStatusEnum.selesai)
    total_dibatalkan = sum(1 for o in orders_today if o.status == OrderStatusEnum.dibatalkan)

    # Breakdown per status
    status_count = OrderStatusCount(
        menunggu=sum(1 for o in orders_today if o.status == OrderStatusEnum.menunggu),
        diproses=sum(1 for o in orders_today if o.status == OrderStatusEnum.diproses),
        selesai=total_selesai,
        dibatalkan=total_dibatalkan,
    )

    # ===== Pendapatan hari ini (dari payment, bukan total_harga order) =====
    pendapatan_hari_ini = (
        db.query(func.coalesce(func.sum(Payment.amount), 0))
        .filter(Payment.paid_at >= today_start)
        .scalar()
    )

    # ===== Status meja =====
    total_meja = db.query(func.count(Meja.id)).scalar()
    meja_terisi = db.query(func.count(Meja.id)).filter(Meja.is_tersedia == False).scalar()
    meja_tersedia = total_meja - meja_terisi

    # ===== Menu populer (top 5 all time) =====
    menu_populer_query = (
        db.query(
            Menu.id.label("menu_id"),
            Menu.nama.label("nama"),
            func.coalesce(func.sum(OrderItem.jumlah), 0).label("total_terjual"),
        )
        .join(OrderItem, OrderItem.menu_id == Menu.id)
        .join(Orders, Orders.id == OrderItem.order_id)
        .filter(Orders.status != OrderStatusEnum.dibatalkan)
        .group_by(Menu.id, Menu.nama)
        .order_by(func.sum(OrderItem.jumlah).desc())
        .limit(5)
        .all()
    )

    menu_populer = [
        MenuPopuler(menu_id=row.menu_id, nama=row.nama, total_terjual=row.total_terjual)
        for row in menu_populer_query
    ]

    # ===== Pendapatan 7 hari terakhir (untuk chart) =====
    seven_days_ago = today_start - timedelta(days=6)  # termasuk hari ini = 7 hari

    pendapatan_7_hari_query = (
        db.query(
            cast(Payment.paid_at, Date).label("tanggal"),
            func.coalesce(func.sum(Payment.amount), 0).label("total"),
        )
        .filter(Payment.paid_at >= seven_days_ago)
        .group_by(cast(Payment.paid_at, Date))
        .order_by(cast(Payment.paid_at, Date))
        .all()
    )

    # Buat dict dari hasil query
    pendapatan_dict = {str(row.tanggal): row.total for row in pendapatan_7_hari_query}

    # Isi 7 hari lengkap (termasuk hari tanpa transaksi = 0)
    pendapatan_7_hari = []
    for i in range(7):
        day = seven_days_ago + timedelta(days=i)
        tanggal_str = day.strftime("%Y-%m-%d")
        total = pendapatan_dict.get(tanggal_str, Decimal("0"))
        pendapatan_7_hari.append(PendapatanPerHari(tanggal=tanggal_str, total=total))

    # ===== Build response =====
    return DashboardSummary(
        total_order_hari_ini=total_order_hari_ini,
        total_pendapatan_hari_ini=Decimal(str(pendapatan_hari_ini)),
        total_order_selesai_hari_ini=total_selesai,
        total_order_dibatalkan_hari_ini=total_dibatalkan,
        total_meja=total_meja,
        meja_terisi=meja_terisi,
        meja_tersedia=meja_tersedia,
        order_status=status_count,
        menu_populer=menu_populer,
        pendapatan_7_hari=pendapatan_7_hari,
    )
