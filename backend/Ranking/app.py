import os
import traceback
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Union, Optional, Tuple
import uvicorn
import requests
from dotenv import load_dotenv
from services import fetch_user_preferences  # Assuming this exists in services.py
from RBS import EventRanking  # Assuming this exists in RBS.py
from supabase import create_client, Client

app = FastAPI(debug=True)

# Configure CORS for Fly.io and local dev
origins = [
    "https://ventaura-backend-rayfould.fly.dev",
    "https://ventaura-ranking-rayfould.fly.dev",
    "http://localhost:5152",
    "http://127.0.0.1:5152",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables
load_dotenv()


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)



# Middleware to catch and log exceptions
@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        print("\n=== Error Traceback ===")
        print(traceback.format_exc())
        print("=====================\n")
        raise e

# Define required columns (used in validation)
required_columns = {
    'events_df': ['contentId', 'title', 'description', 'location', 'start',
                  'source', 'type', 'currencyCode', 'amount', 'url', 'distance'],
    'user_df': ['user_id', 'preferred_events', 'undesirable_events',
                'city', 'latitude', 'longitude', 'max_distance',
                'price_range', 'preferred_crowd_size', 'age']
}

# Pydantic models (unchanged from your original)
class Coordinates(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

class UserLocation(BaseModel):
    city: str = Field(..., min_length=1, max_length=50)
    coordinates: Coordinates

class User(BaseModel):
    user_id: int = Field(..., gt=0)
    preferred_events: Union[str, List[str]]
    undesirable_events: Union[str, List[str]]
    location: UserLocation
    max_distance: float = Field(..., gt=0)
    price_range: Optional[str]
    preferred_crowd_size: str
    age: int = Field(..., gt=0, lt=120)

class Event(BaseModel):
    event_id: int = Field(..., gt=0)
    event_type: str
    distance: float = Field(..., ge=0)
    date_time: str
    popularity: int = Field(..., ge=0)
    price: float = Field(..., ge=0)

class RankedEvent(Event):
    rank: int
    score: float

# Helper functions
def normalize_event_type(event_type):
    if pd.isna(event_type):
        return np.nan
    return event_type.lower().rstrip('s')

def validate_dataframe_columns(df: pd.DataFrame, expected_columns: List[str], df_name: str) -> bool:
    missing_columns = set(expected_columns) - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing columns in {df_name}: {missing_columns}")
    return True

def validate_input(user_id: int, events_df: pd.DataFrame) -> Tuple[pd.DataFrame, bool]:
    if not isinstance(user_id, int) or user_id <= 0:
        raise ValueError("Invalid user_id")

    required_event_columns = set(required_columns['events_df'])
    if not set(events_df.columns).issuperset(required_event_columns):
        missing_cols = required_event_columns - set(events_df.columns)
        raise ValueError(f"Missing columns: {missing_cols}")

    for col in required_event_columns:
        if col == 'start':
            events_df[col] = pd.to_datetime(events_df[col])
        elif col == 'amount':
            events_df[col] = pd.to_numeric(events_df[col], errors='coerce')

    return events_df, True

# Main ranking endpoint
@app.post("/rank-events/{user_id}")
async def rank_events(user_id: int) -> dict:
    print(f"Rank events called with user_id: {user_id}")
    try:
        # Fetch user preferences from C# backend
        user_preferences = await fetch_user_preferences(user_id)
        print(f"Fetched user preferences: {user_preferences}")

        # Format the user preferences
        formatted_user = {
            'Preferences': frozenset(
                normalize_event_type(p.strip())
                for p in user_preferences.Preferences.split(',')
                if p.strip()
            ),
            'Disliked': frozenset(
                normalize_event_type(d.strip())
                for d in user_preferences.Dislikes.split(',')
                if d.strip()
            ),
            'Price Range': user_preferences.PriceRange,
            'Max Distance': user_preferences.MaxDistance
        }
        print(f"Formatted user preferences: {formatted_user}")

        # Fetch CSV from ventaura-backend
        backend_url = os.getenv("BACKEND_URL", "https://ventaura-backend-rayfould.fly.dev")
        csv_url = f"{backend_url}/api/combined-events/get-csv?userId={user_id}"
        response = requests.get(csv_url)
        if response.status_code != 200:
            raise HTTPException(
                status_code=404,
                detail=f"No events file found for user {user_id} at {csv_url}"
            )

        # Write CSV to temporary file (Fly.io's writable dir)
        temp_csv_path = f"/tmp/{user_id}.csv"
        with open(temp_csv_path, "w") as f:
            f.write(response.text)

        # Load and rank events
        ranker = EventRanking(debug_mode=True)
        events_df = pd.read_csv(temp_csv_path, encoding='utf-8-sig')
        ranker.load_events(events_df)
        events_removed = ranker.filter_events()

        result = ranker.rank_events(formatted_user)
        ranked_df = result[0]

        # Save ranked events to temp file
        output_path = "/tmp"
        ranker.save_ranked_events(user_id, ranked_df, output_path)

        return {
            "success": True,
            "message": f"Successfully ranked events for user {user_id}",
            "events_processed": len(ranked_df),
            "events_removed": events_removed
        }

    except Exception as e:
        print(f"ERROR: {str(e)}")
        print(f"Traceback:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

# Test endpoints
@app.get("/test")
async def test():
    return {"message": "API is working"}

@app.get("/")
async def root():
    print("Root endpoint called")
    return {"message": "API is running"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 80))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="debug")