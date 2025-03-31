# services.py

import httpx
from models import UserPreferences
from fastapi import HTTPException
import os

C_SHARP_BACKEND_URL = os.getenv("C_SHARP_BACKEND_URL", "https://ventaura-backend-rayfould.fly.dev")
async def fetch_user_preferences(user_id: int) -> UserPreferences:
    url = f"{C_SHARP_BACKEND_URL}/api/users/{user_id}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            print(f"Raw JSON response: {data}")
            preferences = UserPreferences.parse_obj(data)
            return preferences
        except httpx.RequestError as exc:
            print(f"An error occurred while requesting {exc.request.url!r}.")
            raise HTTPException(status_code=503, detail="Service Unavailable: Unable to reach User service.")
        except httpx.HTTPStatusError as exc:
            print(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.")
            if exc.response.status_code == 404:
                raise HTTPException(status_code=404, detail="User not found.")
            else:
                raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
        except Exception as exc:
            print(f"Unexpected error: {exc}")
            raise HTTPException(status_code=500, detail="Internal Server Error: Unexpected error while fetching user data.")