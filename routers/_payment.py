from datetime import datetime
import json
import random
from typing import Annotated, Any, Dict
from urllib.parse import parse_qs
from uuid import UUID
from fastapi import APIRouter, Body, Depends, HTTPException,Request,status
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select

from crud.product_crud_operations import ProductCrudOperations
from crud.user_crud_operations import UserCrudOperations
from db.database import get_db
from models.product_model import PaymentToken
from models.user_models import User
from operations.basket_operations import get_basket_uuid
from operations.payment_operations import payment
from schemas.product_schemas import EcommerceBase, OpenToken, PaymentStatusOut
import iyzipay

from security.security_funcs import get_current_user_verified

router = APIRouter()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@router.post(
    "/payment",
    response_class=JSONResponse,
    description="This route processes payment using Iyzico. It retrieves the payment token from the request body and verifies the payment status.",
    tags=["Payment"],
    responses={
        200: {
            "description": "Payment processed successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success"
                    }
                }
            }
        },
        401: {
            "description": "Unauthorized - User not authenticated",
            "content": {
                "application/json": {
                    "example": {
                        "message": "User Should Be Verificated"
                    }
                }
            }
        },
        400: {
            "description": "Bad Request - Invalid payment token",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Invalid payment token"
                    }
                }
            }
        }
    }
)
async def payment_func(
    request: Request,
):
    # İstek gövdesini oku
    body = await request.body()
    # Bytes'ı çözümle ve string'e çevir
    body_str = body.decode("utf-8")
    # URL-encoded veriyi çözümle
    parsed_body = parse_qs(body_str)
    # token anahtarını al
    token = parsed_body.get("token", [None])[0]

    async with get_db() as db:
        result = await db.execute(select(PaymentToken).filter(PaymentToken.token == token))
        open_token=  result.scalars().first()
    
    if open_token.status == 1:
        return RedirectResponse(f"http://localhost:3000/payment?status=failed")
    
    user_id = open_token.user_id

    request2 = {
        'locale': 'tr',
        'token': token
    }
    options = {
        'api_key': 'sandbox',
        'secret_key': 'sandbox',
        'base_url': 'sandbox-api.iyzipay.com'
    }

    checkout_form_result = iyzipay.CheckoutForm().retrieve(request2, options)

    payment_json = json.loads(checkout_form_result.read().decode('utf-8'))
    _sum = 0

    if payment_json['status'] == 'success':
        payment_ = PaymentStatusOut(status="success")
        async with get_db() as db:
            user = await UserCrudOperations(db).get_user(str(user_id))
        async with get_db() as db:
            basket_ = await ProductCrudOperations(db).get_basket_all(user.id)
            if len(basket_) > 1:
                for i in range(len(basket_)):
                    async with get_db() as db:
                        product = await ProductCrudOperations(db).get_product(basket_[i].product_id)
                        _sum += product.product_price * basket_[i].product_pcs
            elif len(basket_) == 1:
                async with get_db() as db:
                    product = await ProductCrudOperations(db).get_product(basket_[0].product_id)
                    _sum += product.product_price * basket_[0].product_pcs

        async with get_db() as db:
            basket = await get_basket_uuid(user.id)
            basket_dict = [item.__dict__ for item in basket]  # Eğer basket bir listeyse
            order_json = json.dumps(basket_dict)
            order_id = random.randrange(1000000000, 9999999999)
            order_ = EcommerceBase(
                order_id=order_id,
                order=order_json,
                address=user.address1,
                tax_id=user.tax_id,
                phone_number=user.phone_number,
                basket_price=_sum,
                order_price=_sum,
                coupon_code="",
                order_date=datetime.utcnow(),
                cargo_id="",
                user_id=user_id
            )

        async with get_db() as db:
            open_token.status = 1
            db.add(open_token)
            await db.commit()
            await db.refresh(open_token)
        
        async with get_db() as db:
            await ProductCrudOperations(db).create_order(order_)
        return RedirectResponse(f"http://localhost:3000/payment?order_id={order_id}&status=success")
    else:
        return RedirectResponse(f"http://localhost:3000/payment?status=failed")

@router.get(
    "/payment",
    response_class=JSONResponse,
    description="This route initiates the Iyzico payment process. It retrieves user and basket information, formats the payment request, and returns a redirect response to the payment page.",
    tags=["Payment"],
    responses={
        200: {
            "description": "Redirect to the payment page successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Redirecting to payment page",
                        "paymentPageUrl": "https://payment.iyzico.com"
                    }
                }
            }
        },
        401: {
            "description": "Unauthorized - User not authenticated",
            "content": {
                "application/json": {
                    "example": {
                        "message": "User Should Be Verificated"
                    }
                }
            }
        },
        405: {
            "description": "Method Not Allowed - Basket is empty",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Basket Is Empty"
                    }
                }
            }
        }
    }
)
async def payment_func(
    request: Request,
    user_id: str = Depends(get_current_user_verified)
):
    if user_id:
        async with get_db() as db:
            user = await UserCrudOperations(db).get_user(str(user_id))
        
        async with get_db() as db:
            basket = await ProductCrudOperations(db).get_basket_all(user.id)

        if user.tax_id is None:
            user.tax_id = "11111111111"

        buyer = {
            'id': str(user.id),
            'name': user.name,
            'surname': user.surname,
            'gsmNumber': user.phone_number,
            'email': user.email,
            'identityNumber': "11111111111",
            'lastLoginDate': '2024-08-08 12:43:35',
            'registrationDate': '2013-04-21 15:12:09',
            'registrationAddress': 'Nidakule Göztepe, Merdivenköy Mah. Bora Sok. No:1',
            'ip': '85.34.78.112',
            'city': 'Istanbul',
            'country': 'Turkey',
            'zipCode': '34732'
        }

        address = {
            'contactName': f'{user.name} {user.surname}',
            'city': 'Istanbul',
            'country': 'Turkey',
            'address': 'Nidakule Göztepe, Merdivenköy Mah. Bora Sok. No:1',
            'zipCode': '34732'
        }

        basket_items = []
        _sum = 0

        if len(basket) > 1:
            for i in range(len(basket)):
                async with get_db() as db:
                    product = await ProductCrudOperations(db).get_product(basket[i].product_id)
                    basket_item_temp = {
                        'id': str(product.product_id),
                        'name': product.product_name,
                        'category1': 'Collectibles',
                        'itemType': 'PHYSICAL',
                        'price': product.product_price * basket[i].product_pcs
                    }
                    _sum += product.product_price * basket[i].product_pcs
                    basket_items.append(basket_item_temp)
                    
        elif len(basket) == 1:
            async with get_db() as db:
                product = await ProductCrudOperations(db).get_product(basket[0].product_id)
                basket_item_temp = {
                    'id': "IDS" + str(product.product_id),
                    'name': product.product_name,
                    'category1': 'Collectibles',
                    'itemType': 'PHYSICAL',
                    'price': product.product_price * basket[0].product_pcs
                }
                _sum += product.product_price * basket[0].product_pcs
                basket_items.append(basket_item_temp)

        if len(basket) == 0:
            raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="Basket is Empty")

        _payment = await payment(buyer, address, basket_items)
        payment_json = json.loads(_payment)
        payment_url = payment_json["paymentPageUrl"]
        open_payment_token = payment_json["token"]

        openToken = PaymentToken(
            token=open_payment_token,
            status=0,
            user_id=user.id
        )
        async with get_db() as db:
            db.add(openToken)
            await db.commit()
            await db.refresh(openToken)

        return {"message":'redirect the frontend',"paymentPageUrl": payment_url}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User Should Be Verificated")



