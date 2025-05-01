from fastapi import  HTTPException, Request
from sqlalchemy import UUID

from crud.product_crud_operations import ProductCrudOperations
from crud.user_crud_operations import UserCrudOperations
from db.database import get_db
from models.product_model import Basket
from schemas.product_schemas import BasketAdd, BasketOut
from security.security_funcs import decode_cookie


async def add_to_basket(request: Request, scheme: BasketAdd):
    async with get_db() as db:
        # Decode the cookie to get the user
        user = await decode_cookie(request)
        
        # Fetch the existing basket item for the user and product
        user_basket = await ProductCrudOperations(db).get_basket(scheme.product_id, user)
        
        if user_basket:
            # Update the quantity of the product
            user_basket.product_pcs += scheme.product_pcs
            try:
                # Add the user_basket instance to the session
                db.add(user_basket)
                await db.commit()
                # Refresh the instance to get the latest data
                await db.refresh(user_basket)
                return user_basket
            except Exception as e:
                print(e)
                raise HTTPException(status_code=500, detail="Error updating basket item")
        else:
            # Create a new basket item if it does not exist
            db_basket = Basket(
                basket_id=scheme.basket_id,
                product_id=scheme.product_id,
                product_pcs=scheme.product_pcs,
                user_id=scheme.user_id
            )
            try:
                db.add(db_basket)
                await db.commit()
                await db.refresh(db_basket)
                return db_basket
            except Exception as e:
                print(e)
                raise HTTPException(status_code=500, detail="Error adding to basket")
            
async def edit_basket(request: Request, scheme: BasketAdd, product_id:int,pcs:int,user_id:str):
    async with get_db() as db:
        # Decode the cookie to get the user
        
        # Fetch the existing basket item for the user and product
        user_basket = await ProductCrudOperations(db).get_basket(product_id, scheme.user_id)
        if user_basket:
            # Update the quantity of the product
            user_basket.product_pcs = pcs
            try:
                if user_basket.product_pcs == 0:
                    this = await delete_basket(user_basket.product_id,scheme.user_id)
                    return this
                # Add the user_basket instance to the session
                db.add(user_basket)
                await db.commit()
                # Refresh the instance to get the latest data
                await db.refresh(user_basket)
                return user_basket
            except Exception as e:
                print(e)
                raise HTTPException(status_code=500, detail="Error updating basket item")
        else:
            # Create a new basket item if it does not exist
            db_basket = Basket(
                basket_id=scheme.basket_id,
                product_id=scheme.product_id,
                product_pcs=scheme.product_pcs,
                user_id=scheme.user_id
            )
            try:
                db.add(db_basket)
                await db.commit()
                await db.refresh(db_basket)
                print(db_basket)
                return db_basket
            except Exception as e:
                print(e)
                raise HTTPException(status_code=500, detail="Error adding to basket")
            
            
async def plus_basket(request: Request, product_id:int):
    async with get_db() as db:
        # Decode the cookie to get the user
        user = await decode_cookie(request)
        
        # Fetch the existing basket item for the user and product
        user_basket = await ProductCrudOperations(db).get_basket(product_id, user)
        
        if user_basket:
            # Update the quantity of the product
            user_basket.product_pcs = user_basket.product_pcs+1
            try:
                # Add the user_basket instance to the session
                db.add(user_basket)
                await db.commit()
                # Refresh the instance to get the latest data
                await db.refresh(user_basket)
                return user_basket
            except Exception as e:
                print(e)
                raise HTTPException(status_code=500, detail="Error updating basket item")
            
async def delete_basket(product_id:int,user_id:UUID):
    async with get_db() as db:
        # Decode the cookie to get the user
        
        # Fetch the existing basket item for the user and product
        user_basket = await ProductCrudOperations(db).get_basket(product_id, user_id)
        
        if user_basket:
            try:
                await db.delete(user_basket)
                await db.commit()
                return {"detail": "Basket item deleted successfully"}
            except Exception as e:
                print(e)
                raise HTTPException(status_code=500, detail="Error deleting basket item")
   
async def get_basket(user_id:UUID):
    async with get_db() as db:
        basket = await ProductCrudOperations(db).get_basket_all(user_id)
        
        basket_data = [{"product_id": item.product_id, "product_pcs": item.product_pcs} for item in basket]
    async with get_db() as db:
        items = []
        for i in range(len(basket_data)):
            item_data = await ProductCrudOperations(db).get_product(basket_data[i]["product_id"])
            item_data_dict ={
                "product_id": basket_data[i]["product_id"],
                "product_name": item_data.product_name,
                "product_pcs": basket_data[i]["product_pcs"],
                "product_photo": item_data.product_photo,
                "product_price": item_data.product_price,
            }
            items.append(item_data_dict)
    return(items)

async def get_basket_uuid(user_id:UUID):
    async with get_db() as db:
        basket = await ProductCrudOperations(db).get_basket_all(user_id)
        basket_data = [{"product_id": item.product_id, "product_pcs": item.product_pcs} for item in basket]
    async with get_db() as db:
        items = []
        for i in range(len(basket_data)):
            item_data = await ProductCrudOperations(db).get_product(int(basket_data[i]["product_id"]))
            print(item_data)
            item_data_dict  = BasketOut(
                product_id= basket_data[i]["product_id"],
                product_name= item_data.product_name,
                product_pcs= basket_data[i]["product_pcs"],
                product_price= item_data.product_price,
            )
            items.append(item_data_dict)
    return(items)
