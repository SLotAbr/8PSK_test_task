import pytest
import pytest_asyncio
from asyncio import get_event_loop
from httpx import ASGITransport, AsyncClient
from models import Base, DataRequest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app import app, writeDataRequest
from session import getAsyncSession


@pytest_asyncio.fixture(autouse=True, scope="session")
def event_loop():
	loop = get_event_loop()
	yield loop
	loop.close()


@pytest_asyncio.fixture(scope="session")
async def session_example():
	engine = create_async_engine("sqlite+aiosqlite://", future=True)
	async with engine.begin() as conn:
		await conn.run_sync(Base.metadata.drop_all)
		await conn.run_sync(Base.metadata.create_all)

	AsyncSessionFactory = async_sessionmaker(
		bind=engine, class_=AsyncSession, expire_on_commit=False
	)
	async with AsyncSessionFactory() as session:
		yield session

	async with engine.begin() as conn:
		await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="session")  
async def client(session_example: AsyncSession):
	def getSessionOverride():
		return session_example

	app.dependency_overrides[getAsyncSession] = getSessionOverride

	transport = ASGITransport(app=app)
	async with AsyncClient(
		transport=transport, base_url="http://test"
	) as client_agent:
		yield client_agent

	app.dependency_overrides.clear()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_db_accessibility():
	requestObject = writeDataRequest(
		address = "TTzPiwbBedv7E8p4FkyPyeqq4RVoqRL3TW",
		bandwidth = 123.456,
		energy = 0,
		trx_balance = 123.456,
	)
	assert requestObject != None


# pytest -m unit
# pytest -m "not unit"
# pytest -m integration
# pytest -m "not integration"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_endpoints(client):
	ADDRESS1 = "TTzPiwbBedv7E8p4FkyPyeqq4RVoqRL3TW"
	ADDRESS2 = "TJRabPrwbZy45sbavfcjinPJC18kjpRTv8"

	payload = {"address": ADDRESS1}
	response = await client.post("/address_info", json=payload)
	assert response.status_code == 201

	payload = {"address": ADDRESS2}
	response = await client.post("/address_info", json=payload)
	assert response.status_code == 201

	response = await client.get("/address_info")
	assert response.status_code == 200

	response = await client.get("/address_info?page=1")
	assert response.status_code == 200

	response = await client.get("/address_info?page=2")
	assert response.status_code == 200
