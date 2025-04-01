from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime


Base = declarative_base()


class DataRequest(Base):
	__tablename__ = "requests"

	id = Column(Integer, primary_key=True)
	address = Column(String)
	bandwidth = Column(Float)
	energy = Column(Float)
	trx_balance = Column(Float)
	request_date = Column(DateTime, default=datetime.utcnow)
