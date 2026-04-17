# Pydantic schemas for API responses
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime

# Basic schemas for API responses (no database operations)

class VitalBase(BaseModel):
    type: str
    value: float
    unit: str
    timestamp: datetime

class Vital(VitalBase):
    id: int
    class Config:
        from_attributes = True

class LabResultBase(BaseModel):
    test_name: str
    result: str
    unit: str
    reference_range: Optional[str]
    timestamp: datetime

class LabResult(LabResultBase):
    id: int
    class Config:
        from_attributes = True

class MedicationBase(BaseModel):
    name: str
    dosage: str
    frequency: str
    start_date: date
    end_date: Optional[date]

class Medication(MedicationBase):
    id: int
    class Config:
        from_attributes = True

class ReportBase(BaseModel):
    title: str
    content: str
    created_at: datetime

class Report(ReportBase):
    id: int
    class Config:
        from_attributes = True

class AlertBase(BaseModel):
    message: str
    severity: str
    created_at: datetime
    resolved: bool = False

class Alert(AlertBase):
    id: int
    class Config:
        from_attributes = True

class MessageBase(BaseModel):
    role: str
    content: str
    timestamp: datetime

class Message(MessageBase):
    id: int
    class Config:
        from_attributes = True

class ConversationBase(BaseModel):
    title: str
    created_at: datetime

class Conversation(ConversationBase):
    id: int
    messages: List[Message] = []
    class Config:
        from_attributes = True

class PatientBase(BaseModel):
    name: str
    dob: date
    gender: str
    contact: Optional[str]
    address: Optional[str]

class Patient(PatientBase):
    id: int
    vitals: List[Vital] = []
    lab_results: List[LabResult] = []
    medications: List[Medication] = []
    reports: List[Report] = []
    alerts: List[Alert] = []
    conversations: List[Conversation] = []
    class Config:
        from_attributes = True