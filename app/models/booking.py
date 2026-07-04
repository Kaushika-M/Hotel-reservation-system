from sqlalchemy import Column,Integer,String,Date
from app.database.database import Base

class Booking(Base):
    __tablename__="bookings"
    id=Column(Integer,primary_key=True,index=True)
    customer_id=Column(Integer,nullable=False)
    room_id=Column(Integer,nullable=False)
    check_in=Column(Date,nullable=False)
    check_out=Column(Date,nullable=False)
    price=Column(Integer,nullable=False)
    status=Column(String,nullable=False)