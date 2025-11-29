from sqlalchemy import Column, Integer, String
from db import Base

class InputStore(Base):
    __tablename__ = "inputs"

    id = Column(Integer, primary_key=True, index=True)
    value = Column(String, nullable=False)
