from fastapi import FastAPI, Depends, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse
from sqlalchemy.orm import Session
import xml.etree.ElementTree as ET
import os
from fastapi.templating import Jinja2Templates

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

from database import SessionLocal, Patient, Doctor, Appointment, init_db

app = FastAPI()

init_db()


# --------- DB DEPENDENCY ---------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ===================== HTML =====================

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ===================== PATIENTS =====================

@app.get("/patients", response_class=HTMLResponse)
def get_patients(request: Request, db: Session = Depends(get_db)):
    patients = db.query(Patient).all()
    return templates.TemplateResponse("patients.html", {"request": request, "patients": patients})


@app.post("/patients/add")
def add_patient(name: str = Form(...), age: int = Form(...), diagnosis: str = Form(...), db: Session = Depends(get_db)):
    patient = Patient(name=name, age=age, diagnosis=diagnosis)
    db.add(patient)
    db.commit()
    return {"status": "added"}


# ===================== DOCTORS =====================

@app.get("/doctors", response_class=HTMLResponse)
def get_doctors(request: Request, db: Session = Depends(get_db)):
    doctors = db.query(Doctor).all()
    return templates.TemplateResponse("doctors.html", {"request": request, "doctors": doctors})


@app.post("/doctors/add")
def add_doctor(name: str = Form(...), specialty: str = Form(...), db: Session = Depends(get_db)):
    doctor = Doctor(name=name, specialty=specialty)
    db.add(doctor)
    db.commit()
    return {"status": "added"}


# ===================== APPOINTMENTS =====================

@app.get("/appointments", response_class=HTMLResponse)
def get_appointments(request: Request, db: Session = Depends(get_db)):
    appointments = db.query(Appointment).all()
    return templates.TemplateResponse("appointments.html", {"request": request, "appointments": appointments})


@app.post("/appointments/add")
def add_appointment(date: str = Form(...), patient_id: int = Form(...), doctor_id: int = Form(...), db: Session = Depends(get_db)):
    a = Appointment(date=date, patient_id=patient_id, doctor_id=doctor_id)
    db.add(a)
    db.commit()
    return {"status": "added"}


# ===================== XML EXPORT =====================

@app.get("/export/patients")
def export_patients(db: Session = Depends(get_db)):
    patients = db.query(Patient).all()

    root = ET.Element("patients")

    for p in patients:
        item = ET.SubElement(root, "patient")
        ET.SubElement(item, "id").text = str(p.id)
        ET.SubElement(item, "name").text = p.name
        ET.SubElement(item, "age").text = str(p.age)
        ET.SubElement(item, "diagnosis").text = p.diagnosis

    file_path = "patients.xml"
    tree = ET.ElementTree(root)
    tree.write(file_path, encoding="utf-8", xml_declaration=True)

    return FileResponse(file_path, filename="patients.xml")


# ===================== XML IMPORT =====================

@app.post("/import/patients")
def import_patients(db: Session = Depends(get_db)):
    if not os.path.exists("patients.xml"):
        return {"error": "file not found"}

    tree = ET.parse("patients.xml")
    root = tree.getroot()

    for elem in root.findall("patient"):
        p = Patient(
            name=elem.find("name").text,
            age=int(elem.find("age").text),
            diagnosis=elem.find("diagnosis").text
        )
        db.add(p)

    db.commit()

    return {"status": "imported"}