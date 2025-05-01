
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request 
from fastapi.responses import JSONResponse

from crud.user_crud_operations import UserCrudOperations
from db.database import get_db
from schemas.user_schemas import RegisterInput, RegisterOutput, Token
from security.auth import create_new_user, login, send_otp_
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from cachetools import TTLCache

from security.security_funcs import get_current_user


router = APIRouter()
otp_cache = TTLCache(maxsize=100, ttl=300)  # 5 dakika geçerli
otp_limit = TTLCache(maxsize=100, ttl=300)  # 5 dakika geçerli

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post(
    "/register",
    response_model=RegisterOutput,
    response_class=JSONResponse,
    description="This Route is for registering a new user.",
    tags=["Auth"],
    summary="Register a new user",
    responses={
        200: {
            "description": "User successfully registered",
            "content": {"application/json": {"example": {"message": "User registered successfully"}}}
        },
        400: {
            "description": "Bad Request - Invalid input data",
            "content": {"application/json": {"example": {"detail": "Invalid input data"}}}
        },
        409: {
            "description": "Conflict - User with this email or phone number already exists",
            "content": {"application/json": {"example": {"detail": "User already exists"}}}
        },
        500: {
            "description": "Internal Server Error - An unexpected error occurred",
            "content": {"application/json": {"example": {"detail": "An unexpected error occurred"}}}
        }
    }
)
async def register_user_function(register: RegisterInput):
    """
    Register a new user with the provided information.

    Takes user details including name, surname, email, password, and phone number.
    Returns a response indicating the result of the registration process.
    """
    try:
        response = await create_new_user(
            name=register.name,
            surname=register.surname,
            email=register.email,
            password=register.password,
            phone_number=register.phone_number,
            otp_cache=otp_cache
        )
        print(otp_cache)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print("Exception", e)
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.post(
    "/login",
    response_model=Token,
    response_class=JSONResponse,
    description="This route is for logging in a user and returning an authentication token.",
    tags=["Auth"],
    summary="User login",
    responses={
        200: {
            "description": "User successfully logged in",
            "content": {"application/json": {"example": {"access_token": "jwt_token", "token_type": "bearer"}}}
        },
        400: {
            "description": "Bad Request - Invalid credentials",
            "content": {"application/json": {"example": {"detail": "Invalid email or password"}}}
        },
        401: {
            "description": "Unauthorized - Invalid credentials",
            "content": {"application/json": {"example": {"detail": "Incorrect email or password"}}}
        },
        500: {
            "description": "Internal Server Error - An unexpected error occurred",
            "content": {"application/json": {"example": {"detail": "An unexpected error occurred"}}}
        }
    }
)
async def login_user_function(
    request: Request,
    _login: OAuth2PasswordRequestForm = Depends()):
    """
    Logs in a user by validating their credentials and returns an authentication token.

    Takes the user's email (as username) and password.
    Returns a JWT token if the login is successful.
    """
    try:
        response = await login(email=_login.username, password=_login.password)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print("Exception", e)
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.post("/send_otp", response_class=JSONResponse, tags=["Auth"])
async def send_otp(request: Request, user_id_: UUID = Depends(get_current_user)):
    # Eğer kullanıcı id'si otp_limit içinde yoksa, varsayılan değeri 0 olarak ayarla
    if otp_limit.get(user_id_) is None:
        otp_limit[user_id_] = 0

    if otp_limit[user_id_] <= 3:
        response = await send_otp_(user_id=user_id_, otp_cache=otp_cache)
        if response:
            otp_limit[user_id_] += 1  # Başarılı bir gönderim olduğunda sayacı artır
            return {"status": True}
        else:
            raise HTTPException(status_code=500, detail="Sending Failed.")
    else:
        raise HTTPException(status_code=429, detail="Too Many Requests")

@router.post(
    "/verification/{otp}",
    response_class=JSONResponse,
    tags=["Auth"],
    description="This route verifies the user with the provided OTP. It checks if the OTP matches the stored value and updates the user's verification status accordingly.",
    summary="Verify User with OTP",
    responses={
        200: {
            "description": "User verified successfully",
            "content": {
                "application/json": {
                    "example": {
                        "status": "user_verified"
                    }
                }
            }
        },
        400: {
            "description": "Bad Request - Incorrect OTP",
            "content": {
                "application/json": {
                    "example": {
                        "status": "wrong_code"
                    }
                }
            }
        },
        401: {
            "description": "Unauthorized - User not authenticated",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "User should be authenticated"
                    }
                }
            }
        },
        500: {
            "description": "Internal Server Error - An unexpected error occurred",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Verification Error."
                    }
                }
            }
        }
    }
)
async def verification(
    request: Request,
    otp: int,
    user_id: UUID = Depends(get_current_user)
):
    print("SAY HI",user_id)
    try:
        stored_otp = otp_cache[user_id]
        if stored_otp is not None and stored_otp == otp:
            async with get_db() as db:
                response = await UserCrudOperations(db).update_otp(user_id, otp, otp_cache)
                print(response)

            if response:
                return JSONResponse(content={"status": "user_verified"})
            else:
                raise HTTPException(status_code=500, detail="Verification Error.")
        else:
            return JSONResponse(content={"status": "wrong_code"}, status_code=400)
    except KeyError:
        return JSONResponse(content={"status": "wrong_code"}, status_code=400)
    except Exception as e:
        print("Exception", e)
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
