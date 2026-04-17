# Database models module
from sqlalchemy import Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    dob = Column(Date, nullable=False)
    gender = Column(String, nullable=False)
    contact = Column(String)
    address = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Doctor who owns this patient
    vitals = relationship("Vital", back_populates="patient")
    lab_results = relationship("LabResult", back_populates="patient")
    medications = relationship("Medication", back_populates="patient")
    reports = relationship("Report", back_populates="patient")
    alerts = relationship("Alert", back_populates="patient")
    conversations = relationship("Conversation", back_populates="patient")

class Vital(Base):
    __tablename__ = "vitals"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Doctor who owns this data
    timestamp = Column(DateTime)
    type = Column(String)
    value = Column(Float)
    unit = Column(String)
    patient = relationship("Patient", back_populates="vitals")

class LabResult(Base):
    __tablename__ = "lab_results"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Doctor who owns this data
    timestamp = Column(DateTime)
    test_name = Column(String)
    result = Column(String)
    unit = Column(String)
    reference_range = Column(String)
    patient = relationship("Patient", back_populates="lab_results")

class Medication(Base):
    __tablename__ = "medications"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Doctor who owns this data
    name = Column(String)
    dosage = Column(String)
    frequency = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)
    patient = relationship("Patient", back_populates="medications")

class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Doctor who owns this data
    content = Column(Text)
    created_at = Column(DateTime)
    patient = relationship("Patient", back_populates="reports")

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Doctor who owns this data
    message = Column(String)
    severity = Column(String)
    created_at = Column(DateTime)
    resolved = Column(Boolean, default=False)
    patient = relationship("Patient", back_populates="alerts")

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Doctor who owns this data
    title = Column(String)
    created_at = Column(DateTime)
    patient = relationship("Patient", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    role = Column(String)
    content = Column(Text)
    timestamp = Column(DateTime)
    conversation = relationship("Conversation", back_populates="messages")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    medical_license_id = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)