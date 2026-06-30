from sqlalchemy import Column,Integer,String
from app.database.database import Base

class Room(Base):
    __tablename__="rooms"
    id=Column(Integer,primary_key=True,index=True)
    room_num=Column(Integer,nullable=False,unique=True)
    status=Column(String,nullable=False)
    room_type=Column(String,nullable=False)
    price=Column(Integer,nullable=False)
    description=Column(String,nullable=False)
    capacity=Column(Integer,nullable=False)

