import json
import random
import re
from uuid import UUID
from cachetools import TTLCache
from fastapi import HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
import requests

from crud.user_crud_operations import UserCrudOperations
from db.database import get_db
from schemas.user_schemas import RegisterOutput, UserCreate
from security.security_funcs import encode_pwd, generate_cookie, get_user_with_email, send_otp


async def create_new_user(name: str, surname: str, email: str, password: str, phone_number: str,otp_cache:TTLCache):
    async with get_db() as db:
        existing_user = await get_user_with_email(email)

        if existing_user:
            raise HTTPException(status_code=409, detail="User already exists")
        phone_number_ = await format_phone_number(phone_number=phone_number)
        user_create = UserCreate(
            name=name,
            surname=surname,
            email=email, 
            password=password, 
            phone_number=phone_number_,
        )
        
        user = await UserCrudOperations(db).create_user(user_create)

        access_token = await generate_cookie(user.id, "bearer")
        output_model = RegisterOutput(
            name=name,
            surname=surname,
            status="success",
            access_token=access_token
        )
        print(output_model)

        # OTP'yi gönderen route'u çağır
        otp_response = await request_otp(user.id,otp_cache)  # OTP'yi burada alıyoruz
        print(otp_response)
        print(output_model)
        return output_model

async def request_otp(user_id: UUID,otp_cache:TTLCache):
    otp = await send_otp_(user_id,otp_cache)  # Burada cache kullanarak OTP gönderimi yapılacak
    return {"status": "otp_sent", "otp": otp}

async def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("Authorization")
    return response

async def login(email: str, password: str):        
    user = await get_user_with_email(email)
    
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")  # 404 uygun bir kod

    hashed_password = await encode_pwd(password)

    if hashed_password != user.hashed_pwd:
        raise HTTPException(status_code=401, detail="Invalid email or password")  # 401 uygun bir kod
    
    access_token = await generate_cookie(user.id, "bearer")
    
    # JSONResponse nesnesi oluşturma
    response_data = {
        "access_token": access_token,
        "token_type": "bearer"
    }
    
    # JSONResponse'ı döndür
    response = JSONResponse(content=response_data)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response  # JSONResponse nesnesini döndürün

async def send_otp_(user_id: UUID,otp_cache:TTLCache):
    otp = random.randrange(100000, 999999)

    # Kullanıcıdan yeni OTP istendiğinde, mevcut OTP'yi geçersiz kıl
    if user_id in otp_cache:
        del otp_cache[user_id]

    # Yeni OTP'yi cache'e ekle
    otp_cache[user_id] = otp

    # API URL'si
    url = "http://localhost:3000/send-message"
    async with get_db() as db:
        user = await UserCrudOperations(db).get_user(str(user_id))
    # Gönderilecek mesaj ve numara
    data = {
        "number": f"{user.phone_number}",  # Alıcının telefon numarası
        "message": f"Doğrulama Kodunuz: {otp}"  # Göndermek istediğiniz mesaj
    }

    # POST isteği gönderme
    response = requests.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(data))

    # Yanıtı kontrol et
    if response.status_code == 200:
        return True
    else:
        return False
    
async def format_phone_number(phone_number):
    # Tüm boşlukları, parantezleri, tireleri ve noktaları kaldır
    cleaned_number = re.sub(r'[^\d]', '', phone_number)

    # Başında "90" varsa olduğu gibi bırak, yoksa ekle
    if cleaned_number.startswith("90"):
        formatted_number = cleaned_number
    elif cleaned_number.startswith("0"):
        formatted_number = "90" + cleaned_number[1:]
    elif cleaned_number.startswith("9"):
        formatted_number = "90" + cleaned_number
    else:
        formatted_number = "90" + cleaned_number

    return formatted_number
