from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DATABASE_URL = "sqlite:///./medical.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()

# --------- TABLES ---------

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer)
    diagnosis = Column(String)

    appointments = relationship("Appointment", back_populates="patient")


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    specialty = Column(String)

    appointments = relationship("Appointment", back_populates="doctor")


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String)

    patient_id = Column(Integer, ForeignKey("patients.id"))
    doctor_id = Column(Integer, ForeignKey("doctors.id"))

    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")


# --------- INIT DB + SEED DATA ---------

def init_db():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    # заполнение (если пусто)
    if not db.query(Patient).first():
        p1 = Patient(name="Иван Иванов", age=45, diagnosis="Грипп")
        p2 = Patient(name="Анна Смирнова", age=30, diagnosis="Аллергия")

        d1 = Doctor(name="Петров Сергей", specialty="Терапевт")
        d2 = Doctor(name="Сидорова Мария", specialty="Аллерголог")

        db.add_all([p1, p2, d1, d2])
        db.commit()

        a1 = Appointment(date="2026-05-01", patient_id=1, doctor_id=1)
        a2 = Appointment(date="2026-05-02", patient_id=2, doctor_id=2)

        db.add_all([a1, a2])
        db.commit()

    db.close()