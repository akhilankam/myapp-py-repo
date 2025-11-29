from fastapi import FastAPI, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from db import Base, engine, SessionLocal
from models import InputStore

# Auto-create table if missing
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Template directory
templates = Jinja2Templates(directory="src/templates")

# DB Session (per request)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------------------------------------
# HTML FORM
# ---------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

# ---------------------------------------------------------
# FORM SUBMIT → Save to DB
# ---------------------------------------------------------
@app.post("/submit")
def submit_form(
    value: str = Form(...),
    db: Session = Depends(get_db)
):
    record = InputStore(value=value)
    db.add(record)
    db.commit()
    return RedirectResponse("/list", status_code=302)

# ---------------------------------------------------------
# VIEW STORED DATA
# ---------------------------------------------------------
@app.get("/list", response_class=HTMLResponse)
def list_data(request: Request, db: Session = Depends(get_db)):
    records = db.query(InputStore).all()
    return templates.TemplateResponse("list.html", {"request": request, "records": records})
