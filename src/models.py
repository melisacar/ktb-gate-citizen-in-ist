from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, Date, String, Float
from sqlalchemy import UniqueConstraint
from sqlalchemy import create_engine
from config import DATABASE_URL

Base = declarative_base()

# Define the table
class ist_sinir_kapilari_giris_yapan_vatandas(Base):
    __tablename__ = 'ist_sinir_kapilari_giris_yapan_vatandas'
    __table_args__ = (UniqueConstraint('tarih', 'sehir', 'sinir_kapilari', name = 'unique_ist_sinir_kapilari_giris_yapan_vatandas'),
        {'schema': 'etl'}
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    tarih = Column(Date, nullable=False)
    sehir = Column(String, nullable=False)
    sinir_kapilari = Column(String, nullable=False)
    vatandas_sayisi = Column(Float, nullable=True)
    erisim_tarihi = Column(Date, nullable=False)

engine = create_engine(DATABASE_URL, echo=True)

Session = sessionmaker(bind=engine)
