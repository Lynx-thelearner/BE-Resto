from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
from datetime import datetime


class MenuPopuler(BaseModel):
    """Menu yang paling banyak dipesan"""
    menu_id: int
    nama: str
    total_terjual: int

    model_config = {"from_attributes": True}


class PendapatanPerHari(BaseModel):
    """Pendapatan per hari (untuk chart)"""
    tanggal: str          # format: "2026-02-27"
    total: Decimal

    model_config = {"from_attributes": True}


class OrderStatusCount(BaseModel):
    """Jumlah order per status"""
    menunggu: int = 0
    diproses: int = 0
    selesai: int = 0
    dibatalkan: int = 0


class DashboardSummary(BaseModel):
    """Response utama dashboard"""
    # Ringkasan hari ini
    total_order_hari_ini: int = 0
    total_pendapatan_hari_ini: Decimal = Decimal("0")
    total_order_selesai_hari_ini: int = 0
    total_order_dibatalkan_hari_ini: int = 0

    # Status meja
    total_meja: int = 0
    meja_terisi: int = 0
    meja_tersedia: int = 0

    # Breakdown order status (hari ini)
    order_status: OrderStatusCount = OrderStatusCount()

    # Menu terlaris (top 5)
    menu_populer: List[MenuPopuler] = []

    # Pendapatan 7 hari terakhir (untuk chart)
    pendapatan_7_hari: List[PendapatanPerHari] = []

    model_config = {"from_attributes": True}
