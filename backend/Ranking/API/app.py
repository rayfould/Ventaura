from fastapi import FastAPI, HTTPException
from numpy.ma.core import append
from pydantic import *
from typing import *
from  ..config import *
from ..DQL import QNetwork
from ..Event_Ranking_Environment import EventRecommendationEnv
import pytest
from ..DQL_Test import EventTester
from ..RBS import EventRanking

app = FastAPI()

# Define required columns
required_columns = {
    'events_df': ['Event ID', 'Event Type', 'Date/Time',
                  'Price ($)', 'Distance (km)', 'Popularity'],
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

    @field_validator('preferred_events', 'undesirable_events')
    @classmethod
    def split_events(cls, v: str) -> List[str]:
        if isinstance(v, str):
            return [event.strip() for event in v.split(',')]
        return v

    @field_validator('preferred_crowd_size')
    def validate_preferred_crowd_size(cls, v):
        if v not in POPULARITY_RANGES:
            raise ValueError('Invalid crowd size')
        return v



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


# Load model
ranking_service = EventRankingService(model_path=LOAD_MODEL_PATH)

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
    try:
        # Initialize the ranking system
        ranker = EventRanking(debug_mode=True)

        # Construct file path
        input_path = f"API/content/{user_id}.csv"

        # Check if file exists
        if not os.path.exists(input_path):
            raise HTTPException(
                status_code=404,
                detail=f"No events file found for user {user_id}"
            )

        try:
            events_df = pd.read_csv(input_path)
        except pd.errors.EmptyDataError:
            raise HTTPException(
                status_code=400,
                detail=f"Event file for user {user_id} is empty"
            )
        except pd.errors.ParserError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid CSV format in event file for user {user_id}"
            )

        # Load and process events
        ranker.load_events(events_df)
        events_removed = ranker.filter_events()

        # TODO: Load actual user preferences from database
        test_user = {
            'Preferences': frozenset(['concert', 'festival']),
            'Disliked': frozenset(['opera']),
            'Price Range': '$$',
            'Max Distance': 'Local'
        }

        # Rank and save
        ranked_df, _ = ranker.rank_events(test_user)
        ranker.save_ranked_events(user_id, ranked_df)

        return {
            "success": True,
            "message": f"Successfully ranked events for user {user_id}",
            "events_processed": len(ranked_df),
            "events_removed": events_removed
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


