from fastapi import APIRouter ,Depends, HTTPException,Request,status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer

from crud.product_crud_operations import ProductCrudOperations
from db.database import get_db
from operations.basket_operations import  edit_basket, get_basket
from schemas.product_schemas import BasketAdd, ItemChangesOut
from security.security_funcs import  get_current_user_verified

router = APIRouter()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

from fastapi.responses import JSONResponse
from fastapi import status, HTTPException

@router.put(
    "/basket/edit/{item_id}/{pcs}",
    response_class=JSONResponse,
    response_model=ItemChangesOut,
    tags=["Basket"],
    summary="Edit an item in the user's basket",
    description="This endpoint allows a verified user to edit the quantity of a specific item in their basket. "
                "The item is identified by its ID and the desired quantity is provided as a parameter.",
    responses={
        200: {
            "description": "Basket successfully updated",
            "content": {"application/json": {"example": {"status": "basket_changed"}}}
        },
        400: {
            "description": "Bad Request - Invalid item ID or quantity",
            "content": {"application/json": {"example": {"detail": "Invalid item ID or quantity"}}}
        },
        401: {
            "description": "Unauthorized - User should be verified",
            "content": {"application/json": {"example": {"detail": "User Should Be Verified"}}}
        },
        404: {
            "description": "Not Found - Product not found",
            "content": {"application/json": {"example": {"detail": "Product not found"}}}
        },
        500: {
            "description": "Internal Server Error - An unexpected error occurred",
            "content": {"application/json": {"example": {"detail": "An unexpected error occurred"}}}
        }
    }
)
async def add_to_product_in_basket(request: Request, item_id: int, pcs: int, user_id: str = Depends(get_current_user_verified)):
    """
    Edit an item in the user's basket.

    Allows a verified user to change the quantity of a specified item in their basket.
    The item ID and new quantity are provided as parameters.
    """
    async with get_db() as db:
        product = await ProductCrudOperations(db).get_product(item_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

    async with get_db() as db:
        last_id = await ProductCrudOperations(db).get_last_product()
        if last_id is None:
            last_id = 0

        item_data = await ProductCrudOperations(db).get_product(item_id)
        item_data_dict = {
            "product_id": item_data.product_id,
            "product_description": item_data.product_description,
            "product_name": item_data.product_name,
            "product_photo": item_data.product_photo,
            "product_price": item_data.product_price,
        }
        print("User ID:", user_id)
        if user_id:
            add_basket = BasketAdd(
                basket_id=last_id + 1,
                product_id=product.product_id,
                product_pcs=pcs,
                user_id=user_id
            )
            await edit_basket(scheme=add_basket, request=request, product_id=item_id, pcs=pcs, user_id=user_id)
            items = await get_basket(add_basket.user_id)
            return {"status": "basket_changed"}
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User Should Be Verified")
