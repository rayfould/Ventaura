import sys
import os
from fastapi import FastAPI, HTTPException, Request
from numpy.ma.core import append
from pydantic import BaseModel, Field
from typing import *
# Local imports
from config import *
from DQL import QNetwork
from Event_Ranking_Environment import EventRecommendationEnv
from DQL_Test import EventTester
from RBS import EventRanking

app = FastAPI(debug=True) 

# Define required columns
required_columns = {
    'events_df': ['contentId', 'title', 'description', 'location', 'start',
                  'source', 'type', 'currencyCode', 'amount', 'url', 'distance'],
    'user_df': ['user_id', 'preferred_events', 'undesirable_events',
                'city', 'latitude', 'longitude', 'max_distance',
                'price_range', 'preferred_crowd_size', 'age']
}
class Coordinates(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

class UserLocation(BaseModel):
    city: str = Field(..., min_length=1, max_length=50)
    coordinates: Coordinates


class User(BaseModel):
    user_id: int = Field(..., gt=0)
    preferred_events: Union[str, List[str]]  # Accept either string or list
    undesirable_events: Union[str, List[str]]  # Accept either string or list
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



class EventRankingService:
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.q_network = QNetwork(state_size=5, action_size=1000)
        self.q_network.load_state_dict(torch.load(model_path, weights_only=True))
        self.q_network.eval()

    def rank_events(self, user_df: pd.DataFrame, events_df: pd.DataFrame) -> List[RankedEvent]:
        try:
            # Initialize environment
            env = EventRecommendationEnv(events_df, user_df.iloc[0])
            state = env.reset()
            state_tensor = torch.FloatTensor(state).unsqueeze(0)

            # Get Q-values
            with torch.no_grad():
                q_values = self.q_network(state_tensor).squeeze()

            # Get top actions
            top_actions = torch.topk(q_values, k=len(events_df))
            top_indices = top_actions.indices.tolist()
            top_values = top_actions.values.tolist()

            # Create ranked events
            ranked_events = []
            for rank, (idx, q_val) in enumerate(zip(top_indices, top_values), 1):
                event = events_df.iloc[idx]
                ranked_event = RankedEvent(
                    event_id=event['event_id'],
                    event_type=event['event_type'],
                    date_time=event['date_time'],
                    price=event['price'],
                    distance=event['distance'],
                    popularity=event['popularity'],
                    rank=rank,
                    q_value=float(q_val)
                )
                ranked_events.append(ranked_event)

            return ranked_events

        except Exception as e:
            raise ValueError(f"Error ranking events: {str(e)}")

def validate_dataframe_columns(df: pd.DataFrame, expected_columns: List[str], df_name: str) -> bool:
    missing_columns = set(expected_columns) - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing columns in {df_name}: {missing_columns}")
    return True

def validate_input(user_id: int, events_df: pd.DataFrame) -> Tuple[pd.DataFrame, bool]:
    # Validate user_id
    if not isinstance(user_id, int) or user_id <= 0:
        raise ValueError("Invalid user_id")

    # Validate events_df structure
    required_event_columns = set(required_columns['events_df'])
    if not set(events_df.columns).issuperset(required_event_columns):
        missing_cols = required_event_columns - set(events_df.columns)
        raise ValueError(f"Missing columns: {missing_cols}")

    # Validate data types
    for col in required_event_columns:
        if col == 'start':
            events_df[col] = pd.to_datetime(events_df[col])
        elif col == 'amount':
            events_df[col] = pd.to_numeric(events_df[col], errors='coerce')

    return events_df, True  # Assuming all validations pass

@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        print("\n=== Error Traceback ===")
        print(traceback.format_exc())
        print("=====================\n")
        raise e

# Load model
#ranking_service = EventRankingService(model_path=LOAD_MODEL_PATH)

#
# @app.post("/rank-events/")
# async def rank_events(user: User, events: List[Event]) -> List[RankedEvent]:
#     try:
#         # Debug print statements
#         print("\nProcessing request...")
#         print(f"User data: {user.model_dump()}")
#         print(f"Events data: {[event.model_dump() for event in events]}")
#
#         # Convert to DataFrames
#         user_dict = {
#             'User ID': user.user_id,
#             'Preferred Events': user.preferred_events if isinstance(user.preferred_events, str) else ", ".join(
#                 user.preferred_events),
#             'Undesirable Events': user.undesirable_events if isinstance(user.undesirable_events, str) else ", ".join(
#                 user.undesirable_events),
#             'Preferred Location': user.location.city,
#             'Max Distance (km)': user.max_distance,
#             'Price Range': user.price_range,
#             'Preferred Crowd Size': user.preferred_crowd_size,
#             'Age': user.age,
#             'Latitude': user.location.coordinates.latitude,
#             'Longitude': user.location.coordinates.longitude
#         }
#         user_df = pd.DataFrame([user_dict])
#
#         # Convert events with explicit error handling
#         try:
#             events_dict = [event.model_dump() for event in events]
#             events_df = pd.DataFrame(events_dict)
#             print(f"\nInitial events_df columns: {events_df.columns}")
#
#             # Handle datetime conversion
#             events_df['Date/Time'] = pd.to_datetime(events_df['date_time'])
#             print(f"Date/Time column created: {events_df['Date/Time'].head()}")
#
#             # Create timestamp
#             events_df['timestamp'] = events_df['Date/Time'].apply(lambda x: x.timestamp())
#             print(f"Timestamp column created: {events_df['timestamp'].head()}")
#
#             # Rename columns
#             events_df = events_df.rename(columns={
#                 'event_type': 'Event Type',
#                 'event_id': 'Event ID',
#                 'price': 'Price ($)',
#                 'distance': 'Distance (km)',
#                 'popularity': 'Popularity'
#             })
#
#             # Drop original date_time column
#             events_df = events_df.drop('date_time', axis=1)
#
#             print(f"\nFinal events_df columns: {events_df.columns}")
#             print(f"Final events_df:\n{events_df}")
#
#         except KeyError as e:
#             raise HTTPException(status_code=400, detail=f"Missing required column: {str(e)}")
#         except ValueError as e:
#             raise HTTPException(status_code=400, detail=f"Invalid data format: {str(e)}")
#
#         # Initialize tester and get recommendations
#         tester = EventTester(
#             model_path=LOAD_MODEL_PATH,
#             events_df=events_df,
#             user=user_df.iloc[0]
#         )
#
#         recommendations = tester.get_top_recommendations()
#         return recommendations
#
#
#     except Exception as e:
#
#         print(f"Error occurred: {str(e)}")
#
#         print(f"Traceback: {traceback.format_exc()}")
#
#         raise HTTPException(status_code=400, detail=f"Error ranking events: {str(e)}")
@app.post("/rank-events/{user_id}")  
async def rank_events(user_id: int) -> dict:
    print(f"Rank events called with user_id: {user_id}")
    try:
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.dirname(current_dir)  # Go up one level to 'backend'
        input_path = os.path.join(backend_dir, "ventaura_backend", "CsvFiles", f"{user_id}.csv")
        output_path = os.path.join(backend_dir, "ventaura_backend", "CsvFiles")

        # Debug prints
        print(f"Current working directory: {os.getcwd()}")
        print(f"CsvFiles directory exists: {os.path.exists(os.path.join(backend_dir, 'ventaura_backend', 'CsvFiles'))}")
        print(f"Absolute path to CsvFiles: {os.path.abspath(os.path.join(backend_dir, 'ventaura_backend', 'CsvFiles'))}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"__file__ is: {__file__}")
        print(f"Absolute path of __file__: {os.path.abspath(__file__)}")
        print(f"Current_dir: {current_dir}")
        print(f"Looking for CSV at: {input_path}")

        print(f"\n=== Starting ranking process for user {user_id} ===")

        ranker = EventRanking(debug_mode=True)

        print("Ranking system initialized")

        if not os.path.exists(input_path):
            print(f"ERROR: File not found at {input_path}")
            raise HTTPException(
                status_code=404,
                detail=f"No events file found for user {user_id} at {input_path}"
            )

        print("File found, reading CSV...")
        events_df = pd.read_csv(
            input_path,
            sep=',',
            quotechar='"',
            escapechar='\\',
            doublequote=True,
            skipinitialspace=True
        )
        print(f"CSV loaded with {len(events_df)} events")

        print("Loading events into ranker...")
        ranker.load_events(events_df)
        events_removed = ranker.filter_events()
        print(f"Events filtered. Removed {events_removed} events")

        test_user = {
            'Preferences': frozenset(['music', 'festival']),
            'Disliked': frozenset(['opera']),
            'Price Range': '$$',
            'Max Distance': 'Local'
        }
        print(f"Using test user preferences: {test_user}")

        print("Starting ranking process...")
        result = ranker.rank_events(test_user)
        print(f"Ranking complete. Got {len(result)} values from rank_events")
        ranked_df = result[0]
        print(f"Using first dataframe with {len(ranked_df)} events")

        print("Saving ranked events...")
        ranker.save_ranked_events(user_id, ranked_df, output_path)
        print("Events saved successfully")

        return {
            "success": True,
            "message": f"Successfully ranked events for user {user_id}",
            "events_processed": len(ranked_df),
            "events_removed": events_removed
        }

    except HTTPException as he:
        print(f"HTTP Exception: {he.detail}")
        raise he
    except Exception as e:
        print(f"ERROR: {str(e)}")
        print(f"Exception type: {type(e)}")
        import traceback
        print(f"Traceback:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )



# Add middleware for error logging
@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        print("\n=== Error Traceback ===")
        print(traceback.format_exc())
        print("=====================\n")
        raise e

# Your existing endpoint code here...

@app.get("/test")
async def test():
    return {"message": "API is working"}

@app.get("/")
async def root():
    print("Root endpoint called")
    return {"message": "API is running"}

if __name__ == "__main__":
    uvicorn.run(
        app, 
        host="127.0.0.1", 
        port=8000, 
        log_level="debug",
    )
