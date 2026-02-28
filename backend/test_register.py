import asyncio
from httpx import AsyncClient
from main import app

async def test_register():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/auth/register", json={
            "email": "test_script@test.com",
            "password": "password123",
            "nombre": "Test Script"
        })
        print(f"Status: {response.status_code}")
        print(f"Body: {response.text}")

if __name__ == "__main__":
    asyncio.run(test_register())
