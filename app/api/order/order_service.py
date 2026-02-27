from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from decimal import Decimal
from datetime import datetime, timezone
import uuid

from app.models.order.order_schema import OrderCreate, OrderUpdate, OrderItemCreate
from orm_models import Orders, OrderItem, OrderStatusHistory, OrderStatusEnum, Meja, Pegawai, Menu, TipeOrder


def _generate_order_number() -> str:
    """Generate unique order number: ORD-YYYYMMDD-XXXXX"""
    now = datetime.now(timezone.utc)
    unique = uuid.uuid4().hex[:5].upper()
    return f"ORD-{now.strftime('%Y%m%d')}-{unique}"


#=================Getter=================================
def get_all_orders(db: Session) -> List[Orders]:
    return db.query(Orders).all()

def get_order_by_id(db: Session, order_id: int) -> Optional[Orders]:
    return db.query(Orders).filter(Orders.id == order_id).first()

def get_orders_by_status(db: Session, order_status: OrderStatusEnum) -> List[Orders]:
    return db.query(Orders).filter(Orders.status == order_status).all()

def get_orders_by_meja(db: Session, meja_id: int) -> List[Orders]:
    return db.query(Orders).filter(Orders.meja_id == meja_id).all()

def get_orders_by_waiter(db: Session, waiter_id: int) -> List[Orders]:
    return db.query(Orders).filter(Orders.waiter_id == waiter_id).all()

def get_order_status_history(db: Session, order_id: int) -> List[OrderStatusHistory]:
    order = get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order tidak ditemukan.")
    return db.query(OrderStatusHistory).filter(OrderStatusHistory.order_id == order_id).order_by(OrderStatusHistory.changed_at).all()


#=====================Main Function=======================
def create_order(db: Session, payload: OrderCreate):
    # Validasi meja
    meja = None
    
    if payload.tipe_order == TipeOrder.dine_in:
        if not payload.meja_id:
            raise HTTPException(status_code=400, detail="Dine in harus milih meja.")
        
        meja = db.query(Meja).filter(Meja.id == payload.meja_id).first()
        if not meja:
            raise HTTPException(status_code=404, detail="Meja tidak ditemukan.")
        if not meja.is_tersedia:
            raise HTTPException(status_code=400, detail="Meja sedang tidak tersedia.")

    # Validasi waiter
    waiter = db.query(Pegawai).filter(Pegawai.id == payload.waiter_id).first()
    if not waiter:
        raise HTTPException(status_code=404, detail="Waiter tidak ditemukan.")

    # Validasi items tidak boleh kosong
    if not payload.items:
        raise HTTPException(status_code=400, detail="Order harus memiliki minimal 1 item.")

    # Hitung total harga & buat order items
    total_harga = Decimal("0")
    order_items = []

    for item in payload.items:
        menu = db.query(Menu).filter(Menu.id == item.menu_id).first()
        if not menu:
            raise HTTPException(status_code=404, detail=f"Menu dengan id {item.menu_id} tidak ditemukan.")
        if not menu.is_tersedia:
            raise HTTPException(status_code=400, detail=f"Menu '{menu.nama}' sedang tidak tersedia.")
        if menu.current_stok < item.jumlah:
            raise HTTPException(
                status_code=400,
                detail=f"Stok menu '{menu.nama}' tidak cukup. Tersedia: {menu.current_stok}, diminta: {item.jumlah}."
            )

        harga_at_time = menu.harga
        subtotal = harga_at_time * item.jumlah
        total_harga += subtotal

        order_items.append(OrderItem(
            menu_id=item.menu_id,
            jumlah=item.jumlah,
            harga_at_time=harga_at_time,
            catatan=item.catatan
        ))

        # Kurangi stok menu
        menu.current_stok -= item.jumlah

    # Buat order
    new_order = Orders(
        order_number=_generate_order_number(),
        meja_id=payload.meja_id if payload.tipe_order == TipeOrder.dine_in else None,
        waiter_id=payload.waiter_id,
        tipe_order=payload.tipe_order,
        status=OrderStatusEnum.menunggu,
        total_harga=total_harga,
        items=order_items
    )

    # Set meja jadi tidak tersedia (untuk dine_in)
    if payload.tipe_order == TipeOrder.dine_in:
        meja.is_tersedia = False
  
    try:
        db.add(new_order)
        db.flush() #Buat dapatin id order sebelum commit

        # Catat status history awal
        history = OrderStatusHistory(
            order_id=new_order.id,
            status=OrderStatusEnum.menunggu,
            waiter_id=payload.waiter_id
        )

        db.add(history)
        db.commit()
        db.refresh(new_order)

    except Exception:
        db.rollback()
        raise
    
    return new_order


def update_order(db: Session, order_id: int, payload: OrderUpdate):
    order = get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order tidak ditemukan.")

    update_data = payload.model_dump(exclude_unset=True)

    # ====== Handle status update ======
    if "status" in update_data:
        valid_transitions = {
            OrderStatusEnum.menunggu: [OrderStatusEnum.diproses, OrderStatusEnum.dibatalkan],
            OrderStatusEnum.diproses: [OrderStatusEnum.selesai, OrderStatusEnum.dibatalkan],
            OrderStatusEnum.selesai: [],
            OrderStatusEnum.dibatalkan: [],
        }

        new_status = update_data["status"]
        if new_status not in valid_transitions.get(order.status, []):
            raise HTTPException(
                status_code=400,
                detail=f"Tidak bisa mengubah status dari '{order.status.value}' ke '{new_status.value}'."
            )

        order.status = new_status

        if new_status == OrderStatusEnum.selesai:
            order.waktu_selesai = datetime.now(timezone.utc)
            meja = db.query(Meja).filter(Meja.id == order.meja_id).first()
            if meja:
                meja.is_tersedia = True

        if new_status == OrderStatusEnum.dibatalkan:
            for item in order.items:
                menu = db.query(Menu).filter(Menu.id == item.menu_id).first()
                if menu:
                    menu.current_stok += item.jumlah
            meja = db.query(Meja).filter(Meja.id == order.meja_id).first()
            if meja:
                meja.is_tersedia = True

        # Catat history (pakai waiter_id dari order)
        history = OrderStatusHistory(
            order_id=order_id,
            status=new_status,
            waiter_id=order.waiter_id
        )
        db.add(history)

    # ====== Handle meja, tipe_order (hanya saat menunggu) ======
    if "meja_id" in update_data or "tipe_order" in update_data:
        if order.status != OrderStatusEnum.menunggu:
            raise HTTPException(status_code=400, detail="Meja dan tipe order hanya bisa diubah saat status 'menunggu'.")

        if "meja_id" in update_data:
            meja = db.query(Meja).filter(Meja.id == update_data["meja_id"]).first()
            if not meja:
                raise HTTPException(status_code=404, detail="Meja tidak ditemukan.")
            if not meja.is_tersedia:
                raise HTTPException(status_code=400, detail="Meja sedang tidak tersedia.")
            order.meja_id = update_data["meja_id"]

        if "tipe_order" in update_data:
            order.tipe_order = update_data["tipe_order"]

    # ====== Handle items update (hanya saat menunggu) ======
    if "items" in update_data:
        if order.status != OrderStatusEnum.menunggu:
            raise HTTPException(status_code=400, detail="Items hanya bisa diubah saat status 'menunggu'.")

        if not payload.items:
            raise HTTPException(status_code=400, detail="Order harus memiliki minimal 1 item.")

        # Kembalikan stok dari items lama
        for old_item in order.items:
            menu = db.query(Menu).filter(Menu.id == old_item.menu_id).first()
            if menu:
                menu.current_stok += old_item.jumlah

        # Hapus items lama
        db.query(OrderItem).filter(OrderItem.order_id == order_id).delete()

        # Buat items baru & hitung ulang total
        total_harga = Decimal("0")
        new_items = []

        for item in payload.items:
            menu = db.query(Menu).filter(Menu.id == item.menu_id).first()
            if not menu:
                raise HTTPException(status_code=404, detail=f"Menu dengan id {item.menu_id} tidak ditemukan.")
            if not menu.is_tersedia:
                raise HTTPException(status_code=400, detail=f"Menu '{menu.nama}' sedang tidak tersedia.")
            if menu.current_stok < item.jumlah:
                raise HTTPException(
                    status_code=400,
                    detail=f"Stok menu '{menu.nama}' tidak cukup. Tersedia: {menu.current_stok}, diminta: {item.jumlah}."
                )

            harga_at_time = menu.harga
            total_harga += harga_at_time * item.jumlah

            new_items.append(OrderItem(
                order_id=order_id,
                menu_id=item.menu_id,
                jumlah=item.jumlah,
                harga_at_time=harga_at_time,
                catatan=item.catatan
            ))

            menu.current_stok -= item.jumlah

        db.add_all(new_items)
        order.total_harga = total_harga

    db.commit()
    db.refresh(order)
    return order


def delete_order(db: Session, order_id: int):
    order = get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order tidak ditemukan.")

    if order.status not in [OrderStatusEnum.menunggu, OrderStatusEnum.dibatalkan]:
        raise HTTPException(status_code=400, detail="Hanya order 'menunggu' atau 'dibatalkan' yang bisa dihapus.")

    # Jika masih menunggu, kembalikan stok
    if order.status == OrderStatusEnum.menunggu:
        for item in order.items:
            menu = db.query(Menu).filter(Menu.id == item.menu_id).first()
            if menu:
                menu.current_stok += item.jumlah
        # Kembalikan ketersediaan meja
        meja = db.query(Meja).filter(Meja.id == order.meja_id).first()
        if meja:
            meja.is_tersedia = True

    order_number = order.order_number

    # Hapus status history terkait
    db.query(OrderStatusHistory).filter(OrderStatusHistory.order_id == order_id).delete()
    # Hapus order items
    db.query(OrderItem).filter(OrderItem.order_id == order_id).delete()
    # Hapus order
    db.delete(order)
    db.commit()

    return {"detail": f"Order {order_number} berhasil dihapus."}
