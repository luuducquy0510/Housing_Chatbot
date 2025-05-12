from pydantic import BaseModel, Field


class UserInput(BaseModel):
    DistrictName: str
    NearestStation: str
    MinTimeToNearestStation: float
    Area: float
    BuildingYear: int
    Renovation: str
    FloorPlan: str
    TradePrice: float


class UserQuery(BaseModel):
    """
    Model to represent the user query.
    """
    query: str = Field(..., description="The query string provided by the user.")