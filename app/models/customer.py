from sqlalchemy import Column, Integer, String
from app.database.database import Base

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    name=Column(String,nullable=False)
    email=Column(String,nullable=False,unique=True)
    phone_number=Column(String,nullable=False,unique=True)
    password=Column(String,nullable=False) 
    