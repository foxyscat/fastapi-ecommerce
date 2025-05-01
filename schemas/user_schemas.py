from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import List, Optional

class UserBase(BaseModel):
    name: str
    surname: Optional[str] = None
    email: str
    role: Optional[str] = None
    phone_number: Optional[str] = None
    credit: float = 0.0
    session_cookie: Optional[str] = None

class UserListOut(BaseModel):
    name: str
    surname: Optional[str]= None
    email: str
    hashed_pwd: str
    
    tax_id: Optional[str]= None
    role: Optional[str]= None
    credit: float
    reg_date: str
    phone_number: Optional[str] = None
    verified: Optional[bool] = None
    address1: Optional[str] = None
    address2: Optional[str] = None
    id: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: UUID

    class Config:
        orm_mode = True

class RegisterInput(BaseModel):
    name: str
    surname: str
    email: str
    password: str
    phone_number: str

class RegisterOutput(BaseModel):
    name: str
    surname: str
    access_token: str
    status: str

class LoginOutput(BaseModel):
    name: str
    surname: str
    access_token: str
    status: str

class RegisterOutput(BaseModel):
    name: str
    surname: str
    access_token: str
    status: str

class LoginInput(BaseModel):
    username: Optional[str] = None
    phonenumber: Optional[str] = None
    email: Optional[str] = None
    authPwd: str

class Token(BaseModel):
    access_token: str
    token_type: str

class RegisterRequest(BaseModel):
    device_id: str


class UserLoginRequest(BaseModel):
    email: str
    password: str

class UserUpdateRequest(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    session: Optional[str] = None
    role: Optional[str] = None
    phone_number: Optional[str] = None
    credit: Optional[float] = None

class UserLoginResponse(BaseModel):
    access_token: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    phone_number: Optional[str] = None
    tax_id: Optional[str] = None
    address1: Optional[str] = None
    address2: Optional[str] = None

class UserOut(BaseModel):
    id: UUID
    name: str
    surname: Optional[str] = None
    email: str
    role: Optional[str] = None
    phone_number: Optional[str] = None
    tax_id: Optional[str] = None
    address1: Optional[str] = None
    address2: Optional[str] = None
    credit: float
    verified: bool
    reg_date: datetime  # Tarih formatını ihtiyaca göre ayarlayabilirsiniz

    class Config:
        orm_mode = True  # ORM nesneleri ile çalışabilmesi için


class UserOutLocal(BaseModel):
    id: UUID
    name: str
    surname: Optional[str] = None
    email: str
    phone_number: Optional[str] = None
    tax_id: Optional[str] = None
    address1: Optional[str] = None
    address2: Optional[str] = None

    class Config:
        orm_mode = True  # ORM nesneleri ile çalışabilmesi için

class UserUpdateLocal(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    phone_number: Optional[str] = None
    tax_id: Optional[str] = None
    address1: Optional[str] = None
    address2: Optional[str] = None

class InfoOut(BaseModel):
    language: Optional[str] = None
    about_us: Optional[List[dict]] = None
    contact: Optional[List[dict]] = None
    change_and_refund:Optional[List[dict]] = None
    distance_sales_agreement:Optional[List[dict]] = None
    privacy_policy: Optional[List[dict]] = None
