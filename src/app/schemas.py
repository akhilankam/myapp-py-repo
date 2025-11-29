from pydantic import BaseModel

class InputRequest(BaseModel):
    value: str

class InputResponse(BaseModel):
    id: int
    value: str

    class Config:
        orm_mode = True
