from pydantic import BaseModel
from datetime import datetime


class address(BaseModel):
	address: str


class addressInfo(BaseModel):
	bandwidth: float
	energy: float
	trx_balance: float


class addressRequest(BaseModel):
	address: str
	bandwidth: float
	energy: float
	trx_balance: float
	request_date: datetime
