from fastapi import FastAPI, Depends
# from schemas.masjid import Student
from schemas.masjid import StockBerasCreate, StockBerasUpdate, StockBeras, AkadZakat, AkadZakatCreate,AkadZakatInsert
from config.db import conn,SessionLocal
from models.index import stock_beras, akad_zakat, rekap_zakat   
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy import select,text,update,func,delete
from typing import List, Dict, Any
from datetime import datetime

app = FastAPI()

################ Stack Function ######################

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def generate_next_id(db: Session, prefix: str):
    last_id = db.execute(
        text(f"SELECT id_akad FROM akad_zakat WHERE id_akad LIKE :prefix ORDER BY id_akad DESC LIMIT 1"),
        {'prefix': f'{prefix}%'}
    ).scalar()

    if last_id:
        numeric_part = int(last_id[len(prefix) + 1:])  # Skip the hyphen
        next_id = f"{prefix}-{numeric_part + 1:03d}"
    else:
        next_id = f"{prefix}-001"

    return next_id

def generate_next_id_year(db: Session, prefix: str):
    current_year = db.execute(func.year(func.now())).scalar()
    last_id = db.execute(
        text(f"SELECT id_akad FROM akad_zakat WHERE id_akad LIKE :prefix ORDER BY id_akad DESC LIMIT 1"),
        {'prefix': f'{prefix}%'}
    ).scalar()

    if last_id:
        numeric_part = int(last_id[len(prefix) + 1:])  # Skip the hyphen and year
        next_id = f"{prefix}-{numeric_part + 1:03d}-{current_year}"
    else:
        next_id = f"{prefix}-001-{current_year}"

    return next_id

def get_id_beras_by_harga_beras(db: Session, harga_beras: int):
    query = select([stock_beras.c.id_beras]).where(stock_beras.c.harga_beras == harga_beras)
    result = db.execute(query).scalar()
    return result

def get_id_beras(db: Session, harga_beras: str):
    id_beras = db.execute(
        text(f"SELECT id_beras FROM stock_beras WHERE harga_beras = :harga_beras"),
        {'harga_beras': f'{harga_beras}'}
    ).scalar()
    return id_beras

def get_stock_beras(db: Session, harga_beras: str):
    stock_beras = db.execute(
        text(f"SELECT stock FROM stock_beras WHERE harga_beras = :harga_beras"),
        {'harga_beras': f'{harga_beras}'}
    ).scalar()
    return stock_beras

def generate_id_beras(db: Session):
    last_id = db.execute(
        text("SELECT id_beras FROM stock_beras ORDER BY id_beras DESC LIMIT 1")
    ).scalar()

    if last_id:
        numeric_part = int(last_id)
        next_id = numeric_part + 1
    else:
        next_id = 1

    return next_id

################ End Stack Function ######################

################ Stack Route ######################
################ Route Stock Beras ######################
@app.get('/stock-beras', response_model=Dict[str, Any])
async def index(db: Session = Depends(get_db)):
    query = select(stock_beras)
    result = db.execute(query).fetchall()
    
    # Mengkonversi hasil query menjadi format yang dapat di-serialize oleh Pydantic
    data = [{"id_beras": row.id_beras, "nama": row.nama, "harga_beras": row.harga_beras, "stock": row.stock, "tanggal_masuk": row.tanggal_masuk} for row in result]
    
    return {
        "success": True,
        "data": data
    }
@app.post('/tambah-stock',)
async def store(stock_beras_create: StockBerasCreate, db: Session = Depends(get_db)):
    id_beras = generate_id_beras(db)
    data = conn.execute(stock_beras.insert().values(
        id_beras = id_beras,
        nama=stock_beras_create.nama,
        harga_beras=stock_beras_create.harga_beras,
        stock=stock_beras_create.stock,
    ))
    conn.commit()
    if data.is_insert:
        return {
            "success": True,
            "msg":"Stock Beras Store Successfully"
        }
    else:
         return {
            "success": False,
            "msg":"Some Problem"
        }

@app.put('/update-stock/{id}')
async def update(id:int,stock_beras_update:StockBerasUpdate):
     # Dapatkan data yang ada di database
    existing_data = conn.execute(select(stock_beras).where(stock_beras.c.id_beras == id)).first()

    if not existing_data:
        return {"success": False, "msg": "Stock Beras not found"}

    # Buat kamus yang akan diupdate
    update_data = {}

    # Tambahkan nilai ke kamus hanya jika ada nilai yang tidak None
    if stock_beras_update.nama is not None and stock_beras_update.nama != "string":
        update_data['nama'] = stock_beras_update.nama

    if stock_beras_update.harga_beras is not None and stock_beras_update.harga_beras != 0:
        update_data['harga_beras'] = stock_beras_update.harga_beras

    if stock_beras_update.stock is not None and stock_beras_update.stock != 0:
        update_data['stock'] = stock_beras_update.stock

    # Lakukan pembaruan hanya jika ada sesuatu yang diperbarui
    if update_data:
        conn.execute(stock_beras.update().where(stock_beras.c.id_beras == id).values(update_data))
        conn.commit()
        return {"success": True, "msg": "Stock Beras Update Successfully"}

    return {"success": True, "msg": "No changes to update"}

@app.delete('/delete-stock')
async def delete(id:int):
    data=conn.execute(stock_beras.delete().where(stock_beras.c.id_beras==id))
    conn.commit()
    if data:
        return {
            "success": True,
            "msg":"Stock Beras Delete Successfully"
        }
    else:
         return {
            "success": False,
            "msg":"Some Problem"
        }

@app.delete('/truncate-stock')
async def delete():
    data=conn.execute(stock_beras.delete())
    conn.commit()
    if data:
        return {
            "success": True,
            "msg":"Table Stock Beras Delete Successfully"
        }
    else:
         return {
            "success": False,
            "msg":"Some Problem"
        }

@app.get('/search-beras/{search}',response_model=Dict[str, Any])
async def search(id: str, db: Session = Depends(get_db)):
    result = db.execute(select(stock_beras).where(stock_beras.c.id_beras.like('%' + id + '%'))).fetchone()
    data = [{"id_beras": result.id_beras, "nama": result.nama, "harga_beras": result.harga_beras, "stock": result.stock, "tanggal_masuk": result.tanggal_masuk}]

    # conn.commit()
    return {
        "success": True,
        "data":data
    }    

@app.get('/search-beras-harga/{search}',response_model=Dict[str, Any])
async def search(harga_beras: str, db: Session = Depends(get_db)):
    result = db.execute(select(stock_beras).where(stock_beras.c.harga_beras.like('%' + harga_beras + '%'))).fetchone()
    data = [{"id": result.id_beras, "nama": result.nama, "harga_beras": result.harga_beras, "stock": result.stock, "tanggal_masuk": result.tanggal_masuk}]

    # conn.commit()
    return {
        "success": True,
        "data":data
    }

################ End Route Stock Beras ######################
################ Route Akad Zakat ######################

@app.post('/tambah-akad',)
async def store(akad_create: AkadZakatCreate, db: Session = Depends(get_db)):
    if akad_create.harga_beras is not None and akad_create.harga_beras != 0:
        id_akad = generate_next_id(db, 'ZMAH')
        id_beras = get_id_beras(db, akad_create.harga_beras)
        # Hitung jumlah pengurangan stock berdasarkan jumlah_keluarga * 3.5
        pengurangan_stock = akad_create.jumlah_keluarga * 3.5
        jumlah_uang = akad_create.jumlah_keluarga*3.5*akad_create.harga_beras
        # Dapatkan nilai stock terkini
        stock_beras_value = get_stock_beras(db, akad_create.harga_beras)
        stock_terkini = stock_beras_value - pengurangan_stock
        stock={}
        stock['stock'] = stock_terkini
        if stock:
            conn.execute(stock_beras.update().where(stock_beras.c.id_beras == id_beras).values(stock))
            conn.commit()
        data = conn.execute(akad_zakat.insert().values(
            id_akad=id_akad,
            nama_muzzaki=akad_create.nama_muzzaki,
            nama_amil=akad_create.nama_amil,
            id_beras=id_beras,
            harga_beras=akad_create.harga_beras,
            jumlah_keluarga=akad_create.jumlah_keluarga,
            jumlah_literan=None,
            jumlah_uang=jumlah_uang,
            jenis_zakat=akad_create.jenis_zakat,
            jenis_akad=akad_create.jenis_akad,
        ))
        conn.commit()
        id_rekap = generate_next_id_year(db, 'ZMAH')
        rekap = conn.execute(rekap_zakat.insert().values(
            id_rekap=id_rekap,
            id_akad=id_akad,
            nama_muzzaki=akad_create.nama_muzzaki,
            harga_beras=akad_create.harga_beras,
            jumlah_keluarga=akad_create.jumlah_keluarga,
            jumlah_literan=None,
            jumlah_uang=jumlah_uang,
            jenis_zakat=akad_create.jenis_zakat,
            jenis_akad=akad_create.jenis_akad,
        ))
        conn.commit()
    elif akad_create.harga_beras == 0:
        id_akad = generate_next_id(db, 'ZMAH')
        jumlah_literan = akad_create.jumlah_keluarga * 3.5
        data = conn.execute(akad_zakat.insert().values(
            id_akad=id_akad,
            nama_muzzaki=akad_create.nama_muzzaki,
            nama_amil=akad_create.nama_amil,
            harga_beras=None,
            jumlah_keluarga=akad_create.jumlah_keluarga,
            jumlah_literan=jumlah_literan,
            jumlah_uang=None,
            jenis_zakat=akad_create.jenis_zakat,
            jenis_akad=akad_create.jenis_akad,
        ))
        conn.commit()
        id_rekap = generate_next_id_year(db, 'ZMAH')
        rekap = conn.execute(rekap_zakat.insert().values(
            id_rekap=id_rekap,
            id_akad=id_akad,
            nama_muzzaki=akad_create.nama_muzzaki,
            harga_beras=None,
            jumlah_keluarga=akad_create.jumlah_keluarga,
            jumlah_literan=jumlah_literan,
            jumlah_uang=None,
            jenis_zakat=akad_create.jenis_zakat,
            jenis_akad=akad_create.jenis_akad,
        ))
        conn.commit()
    else:
        return {"success": False, "msg": "Invalid value for harga_beras"}

    if data.is_insert:
        return {
            "success": True,
            "msg": "Akad Zakat Store Successfully"
        }
    else:
        return {
            "success": False,
            "msg": "Some Problem"
        }


# #lebih pendek namun masih belum dipahamin alurnya
# @app.post('/tambah-akad1')
# async def store(akad_create: AkadZakatCreate, db: Session = Depends(get_db)):
#     insert_data = akad_create.dict()

#     # Ensure that only valid columns are used for insertion
#     valid_columns = [col.name for col in akad_zakat.columns]
#     insert_data = {key: insert_data[key] for key in valid_columns if key in insert_data}

#     data = conn.execute(akad_zakat.insert().values(**insert_data))
#     conn.commit()

#     if data.is_insert:
#         return {
#             "success": True,
#             "msg": "Akad Zakat Store Successfully"
#         }
#     else:
#         return {
#             "success": False,
#             "msg": "Some Problem"
#         }

@app.get('/akad-zakat', response_model=Dict[str, Any])
async def index(db: Session = Depends(get_db)):
    query = select(akad_zakat)
    result = db.execute(query).fetchall()
    
    # Mengkonversi hasil query menjadi format yang dapat di-serialize oleh Pydantic
    data = [{
        "id_akad": row.id_akad, 
        "nama_muzzaki": row.nama_muzzaki, 
        "nama_amil": row.nama_amil, 
        "id_beras": row.id_beras, 
        "harga_beras": row.harga_beras,
        "jumlah_keluarga": row.jumlah_keluarga,
        "jumlah_literan": row.jumlah_literan,
        "tanggal_akad": row.tanggal_akad,
        "jumlah_uang": row.jumlah_uang,
        "jenis_zakat": row.jenis_zakat,
        "jenis_akad": row.jenis_akad,} 
        for row in result]
    
    return {
        "success": True,
        "data": data
    }

@app.get('/rekap-zakat', response_model=Dict[str, Any])
async def index(db: Session = Depends(get_db)):
    query = select(rekap_zakat)
    result = db.execute(query).fetchall()
    
    # Mengkonversi hasil query menjadi format yang dapat di-serialize oleh Pydantic
    data = [{
        "id_rekap": row.id_rekap,
        "id_akad": row.id_akad, 
        "nama_muzzaki": row.nama_muzzaki,  
        "harga_beras": row.harga_beras,
        "jumlah_keluarga": row.jumlah_keluarga,
        "jumlah_literan": row.jumlah_literan,
        "tanggal_akad": row.tanggal_akad,
        "jumlah_uang": row.jumlah_uang,
        "jenis_zakat": row.jenis_zakat,
        "jenis_akad": row.jenis_akad,
        "tahun":row.tahun} 
        for row in result]
    
    return {
        "success": True,
        "data": data
    }

@app.get('/search-rekap-tahunan/{search}',response_model=Dict[str, Any])
async def search(tahun: str, db: Session = Depends(get_db)):
    result = db.execute(select(rekap_zakat).where(rekap_zakat.c.tahun.like('%' + tahun + '%'))).fetchall()
    data = [{
        "id_rekap": row.id_rekap,
        "id_akad": row.id_akad, 
        "nama_muzzaki": row.nama_muzzaki,  
        "harga_beras": row.harga_beras,
        "jumlah_keluarga": row.jumlah_keluarga,
        "jumlah_literan": row.jumlah_literan,
        "tanggal_akad": row.tanggal_akad,
        "jumlah_uang": row.jumlah_uang,
        "jenis_zakat": row.jenis_zakat,
        "jenis_akad": row.jenis_akad,
        "tahun":row.tahun} 
        for row in result]
    # conn.commit()
    return {
        "success": True,
        "data":data
    }

@app.delete('/delete-rekap-tahunan')
async def delete(tahun:str):
    data=conn.execute(rekap_zakat.delete().where(rekap_zakat.c.tahun==tahun))
    conn.commit()
    if data:
        return {
            "success": True,
            "msg":"Rekap Tahunan Delete Successfully"
        }
    else:
         return {
            "success": False,
            "msg":"Some Problem"
        }

@app.delete('/delete-akad-zakat')
async def delete():
    data=conn.execute(akad_zakat.delete())
    conn.commit()
    if data:
        return {
            "success": True,
            "msg":"Table Akad Zakat Delete Successfully"
        }
    else:
         return {
            "success": False,
            "msg":"Some Problem"
        }


################ End Route Akad Zakat ######################
################ End Stack Route ######################












