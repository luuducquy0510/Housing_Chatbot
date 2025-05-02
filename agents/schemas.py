from pydantic import BaseModel


class UserInput(BaseModel):
    field_1: str
    field_2: str
    field_3: str
    field_4: str