from sqlalchemy import create_engine,MetaData
from sqlalchemy.orm import sessionmaker

engine=create_engine('mysql+mysqlconnector://root@localhost/masjid')
conn = engine.connect()
meta = MetaData()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

