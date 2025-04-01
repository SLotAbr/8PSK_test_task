from tronpy import AsyncTron
import uvicorn
from typing import List
from collections.abc import Sequence
from fastapi import FastAPI, Depends, status, HTTPException
from session import engine, getAsyncSession
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Base, DataRequest
from datetime import datetime
import schemas


class Settings:
	HOST = "127.0.0.1"
	PORT = 8000
	rowsPerPage = 1


app = FastAPI()

# Исключительно для тестового задания. В реальном production окружении 
# создание и изменение БД осуществляется через отдельные скрипты.
# Сейчас Alembic миграции кажутся избыточными для такой малой задачи
@app.on_event("startup")
async def init_tables():
	async with engine.begin() as conn:
		# await conn.run_sync(Base.metadata.drop_all)
		await conn.run_sync(Base.metadata.create_all)


# Функция уже присутствует в официальном репозитории, но пакет 0.5.0 не обновлен
async def get_energy(client: AsyncTron, address: str) -> int:
	"""Query the energy of the account"""
	account_info = await client.get_account_resource(address)
	energy_limit = account_info.get("EnergyLimit", 0)
	energy_used = account_info.get("EnergyUsed", 0)
	return energy_limit - energy_used


async def writeDataRequest(
	address: str, bandwidth: float, energy: float, trx_balance: float,
	session: AsyncSession = Depends(getAsyncSession)
) -> DataRequest:
	newDataRequest = DataRequest(
		address = address,
		bandwidth = bandwidth,
		energy = energy,
		trx_balance = trx_balance,
		request_date = datetime.utcnow()
	)
	session.add(newDataRequest)
	await session.commit()
	return newDataRequest


@app.post(
	"/address_info", 
	response_model=schemas.addressInfo, 
	status_code=status.HTTP_201_CREATED
)
async def get_address_info(
	address: schemas.address, session: AsyncSession = Depends(getAsyncSession)
) -> DataRequest:
	async with AsyncTron(network="nile") as client:
		bandwidth = await client.get_bandwidth(address.address)
		energy = await get_energy(client, address.address)
		trx_balance = await client.get_account_balance(address.address)

	newDataRequest = await writeDataRequest(
		address.address, bandwidth, energy, trx_balance, session
	)
	return newDataRequest


@app.get(
	"/address_info", response_model= List[schemas.addressRequest]
)
async def read_all(
	page: int = 1, session: AsyncSession = Depends(getAsyncSession)
) -> Sequence[DataRequest]:
	skip, limit = Settings.rowsPerPage * (page - 1), Settings.rowsPerPage
	query = select(DataRequest)\
			.order_by(desc(DataRequest.id))\
			.offset(skip).limit(limit) # from skip to skip+limit
	requestList = await session.execute(query)
	return requestList.scalars().all()


if __name__ == "__main__":
	uvicorn.run(app, host=Settings.HOST, port=Settings.PORT)
