from config.db import meta
from sqlalchemy import Table,Column,Integer,String,DateTime,func,Date
from datetime import datetime

stock_beras=Table(
    'stock_beras',meta,
    Column('id_beras',Integer,primary_key=True, autoincrement=True),
    Column('nama',String(255)),
    Column('harga_beras',Integer),
    Column('stock',Integer),
    Column('tanggal_masuk',DateTime,default=func.now())
)

akad_zakat=Table(
    'akad_zakat',meta,
    Column('id_akad',String(255),primary_key=True),
    Column('nama_muzzaki',String(255)),
    Column('nama_amil',String(255)),
    Column('id_beras',Integer),
    Column('harga_beras',Integer),
    Column('jumlah_keluarga',Integer),
    Column('jumlah_literan',Integer),
    Column('tanggal_akad',Date,default=func.now()),
    Column('jumlah_uang',Integer),
    Column('jenis_zakat',String(255)),
    Column('jenis_akad',String(255)),
)

rekap_zakat=Table(
    'rekap_zakat',meta,
    Column('id_rekap',String(255),primary_key=True),
    Column('id_akad',String(255)),
    Column('nama_muzzaki',String(255)),
    Column('jenis_zakat',String(255)),
    Column('jenis_akad',String(255)),
    Column('jumlah_literan',Integer),
    Column('jumlah_uang',Integer),
    Column('harga_beras',Integer),
    Column('jumlah_keluarga',Integer),
    Column('tanggal_akad',Date,default=func.now()),
    Column('tahun',Integer,default=func.extract('year', func.now())),    
)

