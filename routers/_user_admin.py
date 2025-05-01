import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request,status
from fastapi.responses import JSONResponse
from uuid import UUID

from sqlalchemy import select

from crud.product_crud_operations import ProductCrudOperations
from crud.user_crud_operations import UserCrudOperations
from db.database import get_db
from models.user_models import User
from operations.basket_operations import  get_basket_uuid
from schemas.product_schemas import BasketOut, ListOrderOut
from schemas.user_schemas import UserListOut, UserOutLocal, UserUpdateLocal
from security.security_funcs import get_current_user, get_current_user_verified

router = APIRouter()

@router.put(
    "/user/edit",
    response_class=JSONResponse,
    response_model=UserOutLocal,
    description="This route allows editing local users.",
    tags=["User Management"],
    responses={
        200: {
            "description": "User updated successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "user_id": "123",
                        "username": "new_username",
                        "email": "new_email@example.com"
                    }
                }
            }
        },
        401: {
            "description": "UNAUTHORIZED - User should be verified.",
            "content": {
                "application/json": {
                    "example": {
                        "message": "User Should Be Verified"
                    }
                }
            }
        },
        404: {
            "description": "Local User not found.",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Local User not found"
                    }
                }
            }
        },
        400: {
            "description": "Bad Request - Invalid data provided.",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Invalid input data"
                    }
                }
            }
        }
    }
)
async def edit_local_user(local_user_data: UserUpdateLocal, user_id: str = Depends(get_current_user_verified)):
    if user_id:
        async with get_db() as db:
            # Yerel kullanıcıyı güncellemek için update_local_user fonksiyonunu çağırıyoruz
            updated_local_user = await UserCrudOperations(db).update_user_local(
                user_id=user_id, **local_user_data.dict(exclude_unset=True)
            )

            # Eğer yerel kullanıcı bulunamazsa 404 döndürülür
            if not updated_local_user:
                raise HTTPException(status_code=404, detail="Local User not found")

            # Güncellenen yerel kullanıcının verilerini JSON olarak döndür
            return updated_local_user
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User Should Be Verified")

@router.get(
    "/user/get_user",
    response_class=JSONResponse,
    response_model=UserListOut,
    description="This route retrieves details of a specific user.",
    tags=["User Management"],
    responses={
        200: {
            "description": "User details retrieved successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "name": "John",
                        "surname": "Doe",
                        "email": "john.doe@example.com",
                        "hashed_pwd": "hashed_password",
                        "tax_id": "11111111111",
                        "role": "user",
                        "credit": 100.0,
                        "reg_date": "2024-08-08T12:43:35",
                        "phone_number": "1234567890",
                        "verified": True,
                        "address1": "123 Main St",
                        "address2": "Apt 4B",
                        "id": "123"
                    }
                }
            }
        },
        401: {
            "description": "UNAUTHORIZED - User should be verified.",
            "content": {
                "application/json": {
                    "example": {
                        "message": "User Should Be Verified"
                    }
                }
            }
        },
        404: {
            "description": "User not found.",
            "content": {
                "application/json": {
                    "example": {
                        "message": "User not found"
                    }
                }
            }
        }
    }
)
async def get_user(request: Request, user: str = Depends(get_current_user)):
    if user:
        async with get_db() as db:
            print("Retrieving user:", user)
            result = await db.execute(select(User).filter(User.id == user))
            user_list = result.scalars().first()

            # Kullanıcı bulunamazsa 404 hatası döndürülür
            if not user_list:
                raise HTTPException(status_code=404, detail="User not found")

            _users = UserListOut(
                name=user_list.name,
                surname=user_list.surname,
                email=user_list.email,
                hashed_pwd=user_list.hashed_pwd,
                tax_id=user_list.tax_id,
                role=user_list.role,
                credit=user_list.credit,
                reg_date=user_list.reg_date.isoformat(),
                phone_number=user_list.phone_number,
                verified=user_list.verified,
                address1=user_list.address1,
                address2=user_list.address2,
                id=str(user_list.id),
            )
            return _users
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User Should Be Verified")

@router.get(
    "/user/list_orders",
    response_class=JSONResponse,
    response_model=List[ListOrderOut],
    description="This route retrieves a list of orders for the authenticated user.",
    tags=["User Management"],
    responses={
        200: {
            "description": "Orders listed successfully.",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "order_id": 1234567890,
                            "order": "{\"items\":[{\"product_id\":1,\"quantity\":2},{\"product_id\":2,\"quantity\":1}]}",
                            "address": "123 Main St, Apt 4B",
                            "vkn": "11111111111",
                            "phone_number": "1234567890",
                            "basket_price": 150.0,
                            "order_price": 150.0,
                            "coupon_code": "",
                            "order_date": "2024-08-08T12:43:35",
                            "user_id": "123"
                        },
                        {
                            "order_id": 1234567891,
                            "order": "{\"items\":[{\"product_id\":3,\"quantity\":1}]}",
                            "address": "456 Elm St",
                            "vkn": "22222222222",
                            "phone_number": "0987654321",
                            "basket_price": 75.0,
                            "order_price": 75.0,
                            "coupon_code": "SUMMER20",
                            "order_date": "2024-08-09T12:43:35",
                            "user_id": "123"
                        }
                    ]
                }
            }
        },
        401: {
            "description": "UNAUTHORIZED - User should be verified.",
            "content": {
                "application/json": {
                    "example": {
                        "message": "User Should Be Verified"
                    }
                }
            }
        }
    }
)
async def list_orders(request: Request, user: str = Depends(get_current_user_verified)):
    if user:
        async with get_db() as db:
            order_list = await ProductCrudOperations(db).list_orders_user_id(user)
            _list = []
            for i in range(len(order_list)):
                _orders = ListOrderOut(
                    order_id=order_list[i].order_id,
                    order=json.loads(order_list[i].order),
                    address=order_list[i].address,
                    vkn=order_list[i].tax_id,
                    phone_number=order_list[i].phone_number,
                    basket_price=order_list[i].basket_price,
                    order_price=order_list[i].order_price,
                    coupon_code=order_list[i].coupon_code,
                    order_date=order_list[i].order_date.strftime("%Y-%m-%d %H:%M:%S"),
                    user_id=str(order_list[i].user_id)
                )
                _list.append(_orders)
        return JSONResponse(content=[item.dict() for item in _list])
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User Should Be Verified")


@router.get(
    "/user/get_basket",
    response_class=JSONResponse,
    response_model=List[BasketOut],
    description="This route retrieves the user's shopping basket items.",
    tags=["User Management"],
    responses={
        200: {
            "description": "Basket items retrieved successfully.",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "product_id": 1,
                            "product_name": "Product A",
                            "product_price": 50.0,
                            "quantity": 2
                        },
                        {
                            "product_id": 2,
                            "product_name": "Product B",
                            "product_price": 30.0,
                            "quantity": 1
                        }
                    ]
                }
            }
        },
        401: {
            "description": "UNAUTHORIZED - User should be verified.",
            "content": {
                "application/json": {
                    "example": {
                        "message": "User Should Be Verified"
                    }
                }
            }
        }
    }
)
async def get_basket(request: Request, user: UUID = Depends(get_current_user_verified)):
    if user:
        items = await get_basket_uuid(user)
        return items
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User Should Be Verified")
