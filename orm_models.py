from sqlalchemy import Column, Integer, String, DATE, ForeignKey, DECIMAL, Enum, Time, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from database import Base
import enum
from datetime import datetime, timezone

metadata = Base.metadata

#===============================Table-Table yang berhubungan untuk User=============================

#Enum Role User
class RoleEnum(enum.Enum):
    user = "user"
    admin = "admin"
    pegawai = "pegawai"

#Enum jabatan pegawai
class JabatanEnum(enum.Enum):
    manager = "manager"
    waiter = "waiter"
    koki = "koki"
    kasir = "kasir"

class ActiveEnum(enum.Enum):
    aktif = "aktif"
    tidak_aktif = "tidak_aktif"

class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.user, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    pegawai = relationship("Pegawai", back_populates="user", uselist=False)
    
class Pegawai(Base):
    __tablename__ = "pegawai"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, unique=True)
    nama = Column(String, nullable=False)
    jabatan = Column(Enum(JabatanEnum), nullable=False)
    status = Column(Enum(ActiveEnum), default=ActiveEnum.aktif, nullable=False)
    
    user = relationship("User", back_populates="pegawai")
    orders = relationship("Orders", back_populates="waiter")
    
#===============================Table-Table yang berhubungan untuk Menu=============================
class OrderStatusEnum(enum.Enum):
    menunggu = "menunggu"
    diproses  = "diproses"
    selesai = "selesai"
    dibatalkan = "dibatalkan"
    
class TipeOrder(enum.Enum):
    dine_in = "dine_in"
    take_away = "take_away"

class Meja(Base):
    __tablename__ = "meja"
    
    id = Column(Integer, primary_key=True, index=True)
    nomor_meja = Column(String, unique=True, nullable=False)
    kapasitas = Column(Integer, nullable=False)
    is_tersedia = Column(Boolean, default=True, nullable=False)
    
    orders = relationship("Orders", back_populates="meja")
    
class KategoriMenu(Base):
    __tablename__= "kategori_menu"
    
    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String, unique=True, nullable=False)
    
class UpdateStokHarian(Base):
    __tablename__ = "update_stok_harian"
    
    id = Column(Integer, primary_key=True, index=True)
    tanggal = Column(DATE, nullable=False)
    menu_id = Column(Integer, ForeignKey("menu.id"), nullable=False)
    stok = Column(Integer, nullable=False)
    id_pegawai = Column(Integer, ForeignKey("pegawai.id"), nullable=False)
    
class Menu(Base):
    __tablename__ = "menu"
    
    id = Column(Integer, primary_key=True, index=True)
    kategori_id = Column(Integer, ForeignKey("kategori_menu.id"), nullable=False)
    nama = Column(String, unique=True, nullable=False)
    harga = Column(DECIMAL(10, 2), nullable=False)
    current_stok = Column(Integer, nullable=False)
    is_tersedia = Column(Boolean, default=True, nullable=False)
    
    order_items = relationship("OrderItem", back_populates="menu")
    kategori = relationship("KategoriMenu")
    
class Orders(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True, nullable=False)
    meja_id = Column(Integer, ForeignKey("meja.id"), nullable=True)
    waiter_id = Column(Integer, ForeignKey("pegawai.id"), nullable=False)
    tipe_order = Column(Enum(TipeOrder), nullable=False)
    status = Column(Enum(OrderStatusEnum), default=OrderStatusEnum.menunggu, nullable=False)
    total_harga = Column(DECIMAL(10, 2), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    waktu_selesai = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    waiter = relationship("Pegawai", back_populates="orders") 
    items = relationship("OrderItem", back_populates="order")
    meja = relationship("Meja", back_populates="orders")
    payment = relationship("Payment", back_populates="order", uselist=False)
    status_history = relationship("OrderStatusHistory", back_populates="order")
    
class OrderStatusHistory(Base):
    __tablename__ = "order_status_history"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    status = Column(Enum(OrderStatusEnum), nullable=False)
    changed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    waiter_id = Column(Integer, ForeignKey("pegawai.id"), nullable=False)
    
    order = relationship("Orders", back_populates="status_history")
    
class OrderItem(Base):
    __tablename__ = "order_item"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    menu_id = Column(Integer, ForeignKey("menu.id"), nullable=False)
    jumlah = Column(Integer, nullable=False)
    harga_at_time = Column(DECIMAL(10, 2), nullable=False)
    catatan = Column(Text, nullable=True)
    
    order = relationship("Orders", back_populates="items")
    menu = relationship("Menu", back_populates="order_items")
    
#===============================Table-Table yang berhubungan untuk Payment=============================
class PaymentMethod(enum.Enum):
    cash = "cash"
    qris = "qris"
    debit = "debit"
    kredit = "kredit"

class Payment(Base):
    __tablename__ = "payment"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    method = Column(Enum(PaymentMethod), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    paid_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    order = relationship("Orders", back_populates="payment")
    