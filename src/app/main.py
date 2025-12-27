from fastapi import FastAPI, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

# 🔹 ADDED: Import Prometheus ASGI app to expose /metrics endpoint
from prometheus_client import make_asgi_app

from db import Base, engine, SessionLocal
from models import InputStore

# ---------------------------------------------------------
# DB INIT (unchanged)
# ---------------------------------------------------------
Base.metadata.create_all(bind=engine)

app = FastAPI()

# ---------------------------------------------------------
# 🔹 ADDED: PROMETHEUS METRICS ENDPOINT
# Mounts /metrics endpoint for Prometheus scraping.
# This enables ServiceMonitor-based scraping (kube-prometheus-stack).
# ---------------------------------------------------------
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# ---------------------------------------------------------
# TEMPLATES (unchanged)
# ---------------------------------------------------------
templates = Jinja2Templates(directory="templates")

# ---------------------------------------------------------
# DB Session (per request) (unchanged)
# ---------------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------------------------------------
# HEALTH CHECK ENDPOINTS (unchanged)
# ---------------------------------------------------------
@app.get("/healthz")
def liveness():
    """Kubernetes liveness probe"""
    return {"status": "alive"}

@app.get("/ready")
def readiness(db: Session = Depends(get_db)):
    """Kubernetes readiness probe"""
    try:
        db.execute("SELECT 1")
        return {"status": "ready"}
    except Exception as e:
        return {"status": "not_ready", "error": str(e)}, 503

# ---------------------------------------------------------
# HTML FORM (unchanged)
# ---------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

# ---------------------------------------------------------
# FORM SUBMIT → Save to DB (unchanged)
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
# VIEW STORED DATA (unchanged)
# ---------------------------------------------------------
@app.get("/list", response_class=HTMLResponse)
def list_data(request: Request, db: Session = Depends(get_db)):
    records = db.query(InputStore).all()
    return templates.TemplateResponse("list.html", {"request": request, "records": records})
