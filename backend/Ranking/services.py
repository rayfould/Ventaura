# services.py

import httpx
from typing import Optional
from models import UserPreferences
from fastapi import HTTPException
import os

C_SHARP_BACKEND_URL = os.getenv("C_SHARP_BACKEND_URL", "http://localhost:5152")

async def fetch_user_preferences(user_id: int) -> UserPreferences:
    url = f"{C_SHARP_BACKEND_URL}/api/users/{user_id}/preferences"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)  # 10-second timeout
            response.raise_for_status()  # Raise exception for HTTP errors
            print(f"Raw JSON response: {response.json()}")  # Debugging line
            preferences = UserPreferences.parse_obj(response.json())
            return preferences
        except httpx.RequestError as exc:
            # Network-related errors
            print(f"An error occurred while requesting {exc.request.url!r}.")
            raise HTTPException(status_code=503, detail="Service Unavailable: Unable to reach User Preferences service.")
        except httpx.HTTPStatusError as exc:
            # Non-2xx responses
            print(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.")
            if exc.response.status_code == 404:
                raise HTTPException(status_code=404, detail="User preferences not found.")
            else:
                raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
        except Exception as exc:
            # Other errors
            print(f"Unexpected error: {exc}")
            raise HTTPException(status_code=500, detail="Internal Server Error: Unexpected error while fetching user preferences.")
