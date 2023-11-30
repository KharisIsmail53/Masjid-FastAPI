from pydantic import BaseModel,Extra
from typing import Optional
from datetime import datetime,date

class StockBerasBase(BaseModel):
    nama: str
    harga_beras: int
    stock: int

class StockBerasCreate(StockBerasBase):
    pass

class StockBerasUpdate(StockBerasBase):
    pass

class StockBeras(StockBerasBase):
    id_beras: int
    tanggal_masuk: Optional[datetime]

    class Config:
        orm_mode = True


class AkadBase(BaseModel):
    nama_muzzaki: str
    nama_amil: str
    harga_beras: Optional[int] = None
    jumlah_keluarga: int
    jenis_zakat: str
    jenis_akad: str

class AkadZakat(AkadBase):
    id_akad: Optional[str] = None
    id_beras: Optional[int] = None
    tanggal_akad:Optional[date]
    jumlah_literan: Optional[int] = None
    jumlah_uang: Optional[int] = None

    class Config:
        orm_mode = True

class AkadZakatCreate(AkadBase):
    # id_akad: Optional[str] = None
    pass

class AkadZakatInsert(AkadBase):
    pass

