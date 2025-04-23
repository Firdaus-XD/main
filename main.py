from typing import List
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from pydantic import BaseModel
from fastapi.responses import HTMLResponse

app = FastAPI(
    title="API Katalog Teknologi",
    description="API untuk mengelola katalog produk teknologi",
    version="1.0.0",
)

# Koneksi database SQLite
DATABASE_URL = "sqlite:///./tech_catalog.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Model Database
class TechItem(Base):
    __tablename__ = "tech_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    category = Column(String(50))
    price = Column(Integer)
    brand = Column(String(50))
    description = Column(String(500))

# Buat tabel
Base.metadata.create_all(bind=engine)

# Dependency untuk session database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Model Pydantic
class TechItemCreate(BaseModel):
    name: str
    category: str
    price: int
    brand: str
    description: str

class TechItemResponse(BaseModel):
    id: int
    name: str
    category: str
    price: int
    brand: str
    description: str

    class Config:
        orm_mode = True

# Data awal teknologi
initial_tech_items = [
    {
        "name": "MacBook Pro 14-inch",
        "category": "Laptop",
        "price": 1999,
        "brand": "Apple",
        "description": "Laptop profesional dengan chip M1 Pro"
    },
    {
        "name": "iPhone 13 Pro",
        "category": "Smartphone",
        "price": 999,
        "brand": "Apple",
        "description": "Smartphone flagship Apple dengan kamera canggih"
    },
    {
        "name": "Galaxy S22 Ultra",
        "category": "Smartphone",
        "price": 1199,
        "brand": "Samsung",
        "description": "Smartphone premium Samsung dengan S-Pen"
    },
    {
        "name": "XPS 13",
        "category": "Laptop",
        "price": 1299,
        "brand": "Dell",
        "description": "Laptop ultraportabel dengan layar InfinityEdge"
    },
    {
        "name": "PlayStation 5",
        "category": "Gaming Console",
        "price": 499,
        "brand": "Sony",
        "description": "Konsol game generasi terbaru dari Sony"
    },
    {
        "name": "AirPods Pro",
        "category": "Audio",
        "price": 249,
        "brand": "Apple",
        "description": "Earbuds nirkabel dengan noise cancellation"
    },
    {
        "name": "RTX 3080",
        "category": "GPU",
        "price": 699,
        "brand": "NVIDIA",
        "description": "Kartu grafis high-end untuk gaming dan kreator"
    },
    {
        "name": "Kindle Paperwhite",
        "category": "E-Reader",
        "price": 139,
        "brand": "Amazon",
        "description": "E-reader dengan layar anti-silau"
    }
]

# Fungsi untuk inisialisasi data
def initialize_data():
    db = SessionLocal()
    try:
        # Cek apakah tabel sudah ada isinya
        if db.query(TechItem).count() == 0:
            for item in initial_tech_items:
                db_item = TechItem(**item)
                db.add(db_item)
            db.commit()
            print("Data teknologi berhasil diinisialisasi")
    finally:
        db.close()

# Panggil fungsi inisialisasi saat aplikasi mulai
initialize_data()

# Halaman utama
@app.get("/", response_class=HTMLResponse)
async def read_root():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Katalog Teknologi</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            h1 { color: #333; }
            .endpoint { background: #f4f4f4; padding: 10px; margin: 10px 0; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1>Selamat Datang di Katalog Teknologi</h1>
        <p>Gunakan endpoint berikut untuk mengakses API:</p>
        <div class="endpoint"><strong>GET /items/</strong> - Dapatkan semua produk teknologi</div>
        <div class="endpoint"><strong>GET /items/{id}</strong> - Dapatkan produk tertentu</div>
        <div class="endpoint"><strong>POST /items/</strong> - Tambahkan produk baru</div>
        <div class="endpoint"><strong>PUT /items/{id}</strong> - Update produk</div>
        <div class="endpoint"><strong>DELETE /items/{id}</strong> - Hapus produk</div>
        <p>Kunjungi <a href="/docs">/docs</a> untuk dokumentasi interaktif.</p>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# Endpoint API
@app.get("/items/", response_model=List[TechItemResponse])
def read_items(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    items = db.query(TechItem).offset(skip).limit(limit).all()
    return items

@app.get("/items/{item_id}", response_model=TechItemResponse)
def read_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(TechItem).filter(TechItem.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.post("/items/", response_model=TechItemResponse)
def create_item(item: TechItemCreate, db: Session = Depends(get_db)):
    db_item = TechItem(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.put("/items/{item_id}", response_model=TechItemResponse)
def update_item(item_id: int, item: TechItemCreate, db: Session = Depends(get_db)):
    db_item = db.query(TechItem).filter(TechItem.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    for key, value in item.dict().items():
        setattr(db_item, key, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(TechItem).filter(TechItem.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return {"message": "Item deleted successfully"}

# Jalankan dengan: uvicorn main:app --reload