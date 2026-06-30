from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.database.database import Base, engine
from app.models.customer import Customer

from fastapi import Form
from fastapi.responses import RedirectResponse
from app.database.database import SessionLocal

Base.metadata.create_all(bind=engine)

app = FastAPI()

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