from fastapi import FastAPI
import orm_models, database


from app.api import routers
from fastapi.middleware.cors import CORSMiddleware

"""Inisialisai app resto"""
app = FastAPI(
    title="Resto API",
    description="API untuk sistem manajemen restoran",
    version="1.0.0"
)

# Middleware CORS

origins = [
    "http://localhost:8000/",       # Vue lewat nginx
    "http://localhost:3000/",       # kalau kamu running vite dev
    "https://9b48d3833802.ngrok-free.app/",  # URL ngrok backend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

"""Masukin Router"""
for r in routers:
    app.include_router(r)
    
"""Root Endpoint"""
@app.get("/")
def root():
    return {"message": "Welcome to Resto API 🚀"}
