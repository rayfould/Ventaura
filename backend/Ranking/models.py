# models.py

from pydantic import BaseModel, Field
from typing import List, Union

class UserPreferences(BaseModel):
    Preferences: Union[str, List[str]] = Field(..., alias='preferences')
    Dislikes: Union[str, List[str]] = Field(..., alias='dislikes')
    PriceRange: str = Field(..., alias='priceRange')
    MaxDistance: int = Field(..., alias='maxDistance')  

    class Config:
        allow_population_by_field_name = True