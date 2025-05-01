import json
import random
from uuid import UUID
from fastapi.security import OAuth2PasswordBearer
import jwt
from datetime import datetime, timedelta
from fastapi import   Depends, HTTPException, Request
from hashlib import sha256
import requests
from sqlalchemy.future import select

from crud.user_crud_operations import UserCrudOperations
from db.database import get_db
from models.user_models import User

SECRET_KEY = "YourSecretkeyHere"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10080

async def decode_cookie(request: Request):
    jwt_payload = jwt.decode(request.cookies.get("Authorization"), SECRET_KEY, algorithms=[ALGORITHM])
    return jwt_payload["access_token"]

async def decode_str_cookie(_cookie):
    jwt_payload = jwt.decode(_cookie, SECRET_KEY, algorithms=[ALGORITHM])
    return jwt_payload["access_token"]

async def generate_cookie(user_id,type):
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = jwt.encode(
        {"access_token": str(user_id), "token_type":type,"exp": datetime.utcnow() + access_token_expires},
        SECRET_KEY, algorithm=ALGORITHM
    )

    return access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def encode_pwd(pwd):
    salted_password = pwd + SECRET_KEY
    hashed_password = sha256(salted_password.encode("utf-8")).hexdigest()
    
    return hashed_password

async def get_user_with_email(email):
    async with get_db() as db:
        try:
            result = await db.execute(select(User).filter(User.email == email))
        except Exception as e:
            print(e)
        return result.scalars().first()
    
async def check_access_token(request: Request):
    access_token = request.cookies.get("Authorization")
    if access_token:
        try:
            payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
            return True
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False
    return False

async def get_current_user_verified(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id: str = payload.get("access_token")  # Kullanıcı ID'sini 'sub' olarak alıyoruz
    async with get_db() as db:
        user = await UserCrudOperations(db).get_user(user_id=user_id)  # Kullanıcıyı veritabanından al
    if user.verified == True:
        return user.id
    return None
    
async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id: str = payload.get("access_token")  # Kullanıcı ID'sini 'sub' olarak alıyoruz
    async with get_db() as db:
        user = await UserCrudOperations(db).get_user(user_id=user_id)  # Kullanıcıyı veritabanından al
        print(token)
        return user.id

async def get_current_user_role(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id: str = payload.get("access_token")  # Kullanıcı ID'sini 'sub' olarak alıyoruz
    async with get_db() as db:
        user = await UserCrudOperations(db).get_user(user_id=user_id)  # Kullanıcıyı veritabanından al
    return user.role

async def send_otp(user_id:UUID):
    otp = random.randrange(0,999999)
    async with get_db() as db:
        user = await UserCrudOperations(db).get_user(user_id)
        # API URL'si
        url = "http://localhost:3000/send-message"

        # Gönderilecek mesaj ve numara
        data = {
            "number": f"90{user.phone_number}",  # Alıcının telefon numarası
            "message": f"Doğrulama Kodunuz: {otp}"  # Göndermek istediğiniz mesaj
        }

        # POST isteği gönderme
        response = requests.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(data))
        """
        url = "https://api.vatansms.net/api/v1/1toN"

        data = json.dumps({
        "api_id" : "",
        "api_key" : "",
        "sender" : "SMS TEST",
        "message_type" : "turkce",
        "message" : f"Tek Seferlik Doğrulama Kodunuz: {otp}",
        "message_content_type": "bilgi",
        "phones" : [
            user.phone_number
        ]
        })
        headers = {'Content-Type': 'application/json'}

        response = requests.post(url, headers=headers, data=data, verify=False)

        print(response.json()) """
    async with get_db() as db:
        await UserCrudOperations(db).set_otp(user_id=user_id,otp=otp)  # Kullanıcıyı veritabanından al

        return otp