# models.py

from pydantic import BaseModel, Field
from typing import List, Union, Optional

class UserPreferences(BaseModel):
    Preferences: Union[str, List[str]] = Field(..., alias='preferences')
    Dislikes: Union[str, List[str]] = Field(..., alias='dislikes')
    PriceRange: Optional[str] = Field(None, alias='price_range')
    MaxDistance: Optional[str] = Field(None, alias='max_distance')

    class Config:
        allow_population_by_field_name = True
