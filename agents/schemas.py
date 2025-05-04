from pydantic import BaseModel, Field


class UserInput(BaseModel):
    Area: float
    BuildingYear: int
    TimeToNearestStation: float
    DistrictName: str  
    RenovationEncoded: int
    TradePrice: float


class UserQuery(BaseModel):
    """
    Model to represent the user query.
    """
    query: str = Field(..., description="The query string provided by the user.")