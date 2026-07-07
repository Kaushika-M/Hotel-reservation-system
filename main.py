from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.database.database import Base, engine
from app.models.customer import Customer
from app.models.room import Room
from app.models.room import Booking 

from fastapi import Form
from fastapi.responses import RedirectResponse
from app.database.database import SessionLocal

from starlette.middleware.sessions import SessionMiddleware
from datetime import date

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(SessionMiddleware,
    secret_key="my_secret_key"
)

templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "home.html",
        {"request": request}
    )

@app.get("/signup",response_class=HTMLResponse)
def signup(request:Request):
    return templates.TemplateResponse(
        "signup.html",
        {"request": request}
    )

@app.post("/signup")
def signup(
    name:str=Form(...),
    email:str=Form(...),
    phone_number:str=Form(...),
    password:str=Form(...),
    confirm_password:str=Form(...)
):
    if password!=confirm_password:
        return "Passwords do not match"
    db = SessionLocal()
    customer=Customer(
        name = name,
        email = email,
        phone_number = phone_number,
        password = password
    )    
    db.add(customer)
    db.commit()
    db.refresh(customer)
    db.close()

    return RedirectResponse(url="/signin",status_code=303)

@app.get("/signin",response_class=HTMLResponse)
def signup(request:Request):
    return templates.TemplateResponse(
        "signin.html",
        {"request": request}
    )

@app.post("/signin")
def signin(request:Request,
    email:str=Form(...),
    password:str=Form(...)
):
    db=SessionLocal()
    customer = db.query(Customer).filter(Customer.email == email).first()
    if customer is None:
        db.close()
        return "Email not registered"

    if customer.password != password:
        db.close()
        return "Incorrect password"
    request.session["customer_id"]=customer.id
    
    db.close()

    return RedirectResponse(url="/search", status_code=303)

@app.get("/admin", response_class=HTMLResponse)
def admin(request: Request):
    db = SessionLocal()

    rooms = db.query(Room).all()

    db.close()

    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "rooms": rooms
        }
    )

@app.post("/add_room")
def add_room(
    room_num:int=Form(...),
    status:str=Form(...),
    room_type:str=Form(...),
    price:int=Form(...),
    description:str=Form(...),
    capacity:int=Form(...)
):
    db = SessionLocal()

    existing_room = db.query(Room).filter(Room.room_num == room_num).first()

    if existing_room is not None:
        db.close()
        return "Room number already exists"
 
    room=Room(
        room_num=room_num,
        status=status,
        room_type=room_type,
        price=price,
        description=description,
        capacity=capacity
    )    
    db.add(room)
    db.commit()
    db.refresh(room)
    db.close()

    return RedirectResponse(url="/admin",status_code=303)

@app.get("/delete_room/{room_id}")
def delete_room(room_id:int):
    db=SessionLocal()
    room=db.query(Room).filter(Room.id==room_id).first()
    if room is None:
        db.close()
        return "Room Not Found"

    db.delete(room)
    db.commit()
    db.close()
    return RedirectResponse(url="/admin",status_code=303)

@app.get("/edit_room/{room_id}",response_class=HTMLResponse)
def edit_room(request:Request,room_id:int):
    db=SessionLocal()
    room=db.query(Room).filter(Room.id==room_id).first()
    if room is None:
        db.close()
        return "Room Not found"    
    db.close()
    return templates.TemplateResponse(
        "edit_room.html",
        {
            "request": request,
            "room": room
        }
    )

@app.post("/edit_room/{room_id}")
def update_room(room_id: int,
    room_num: int = Form(...),
    room_type: str = Form(...),
    price: int = Form(...),
    capacity: int = Form(...),
    status: str = Form(...),
    description: str = Form(...)
):
    db=SessionLocal()
    room=db.query(Room).filter(Room.id==room_id).first()
    if room is None:
        db.close()
        return "Room not found"

    room.room_num = room_num
    room.room_type = room_type
    room.price = price
    room.capacity = capacity
    room.status = status
    room.description = description

    db.commit() 
    db.close()
    return RedirectResponse(url="/admin",status_code=303)

@app.get("/search",response_class=HTMLResponse)
def search(request:Request,
           room_type:str="",
           capacity:int=None,
           price:int=None
):
    db=SessionLocal()
    query=db.query(Room).filter(Room.status=="Available")
    if room_type:
        query=query.filter(Room.room_type==room_type)
    if capacity:
        query=query.filter(Room.capacity>=capacity)
    if price:
        query = query.filter(Room.price<=price)    

    rooms=query.all()
    if not rooms:
        db.close()
        return "No Available Rooms"

    db.close() 
    return templates.TemplateResponse("search.html",
                                      {"request":request,
                                      "rooms":rooms
                                      })

@app.get("/room/{room_id}",response_class=HTMLResponse)
def detail(request:Request,room_id:int):
    db=SessionLocal()
    customer_id = request.session.get("customer_id")

    if customer_id is None:
        return RedirectResponse(url="/sigin",status_code=303) 
    room=db.query(Room).filter(Room.id==room_id).first()
    if room is None:
        db.close()
        return "Room not found"
    db.close()
    return templates.TemplateResponse("detail.html",
                                     {"request":request,
                                      "room":room})

@app.post("/confirmation/{room_id}")
def confirm_booking(request: Request,room_id: int,
    check_in: date = Form(...),
    check_out: date = Form(...)
):
    db = SessionLocal()

    customer_id = request.session.get("customer_id")

    if customer_id is None:
        db.close()
        return RedirectResponse(url="/signin", status_code=303)

    room = db.query(Room).filter(Room.id == room_id).first()

    if room is None:
        db.close()
        return "Room not found"

    booking = Booking(
        customer_id=customer_id,
        room_id=room.id,
        check_in=check_in,
        check_out=check_out,
        price=room.price,
        status="Confirmed"
    )

    db.add(booking)
    room.status = "Booked"
    db.commit()
    db.close()

    return RedirectResponse(url="/success", status_code=303)

@app.get("/success",response_class=HTMLResponse)
def success(request:Request):
    return templates.TemplateResponse("success.html",
                                      {
                                          "request":request
                                      })

@app.get("/history",response_class=HTMLResponse)
def history(request:Request):
    customer_id=request.session.get("customer_id")
    if bookings is None:
         return RedirectResponse(url="/signin", status_code=303)
    db=SessionLocal()
    bookings=db.query(Booking).filter(Booking.customer_id==customer_id).all()
    
    db.close()
    return templates.TemplateResponse("history.html",
                                     {
                                      "request":request,"bookings":bookings
                                     })