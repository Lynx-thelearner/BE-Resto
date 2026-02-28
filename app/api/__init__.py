from .auth import auth_router
from .user import user_router
from .pegawai import pegawai_router
from .meja import meja_router
from .kategori_menu import kategori_menu_router
from .menu import menu_router
from .order import order_router
from .payment import payment_router
from .stok_harian import stok_harian_router
from .dashboard import dashboard_router

routers = [
    auth_router.router,
    user_router.router,
    pegawai_router.router,
    meja_router.router,
    kategori_menu_router.router,
    menu_router.router,
    order_router.router,
    payment_router.router,
    stok_harian_router.router,
    dashboard_router.router,
]