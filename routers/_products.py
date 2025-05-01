import os
from typing import List, Optional
from fastapi import APIRouter, HTTPException,Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select

from crud.product_crud_operations import ProductCrudOperations
from db.database import get_db
from models.product_model import Product
from schemas.product_schemas import CattegoriesOut, ItemBaseOut

router = APIRouter()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.get(
    "/list_products",
    response_class=JSONResponse,
    response_model=List[ItemBaseOut],
    tags=["Product Management"],
    description="Retrieves a list of products, optionally filtered by minimum and maximum price.",
    responses={
        200: {
            "description": "List of products retrieved successfully.",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "item_name": "Sample Product",
                            "product_id": 1,
                            "product_price": 100.0,
                            "product_description": "A great product.",
                            "product_cattegory": "Category1",
                            "product_stock": 50,
                            "gallery_items": []
                        }
                    ]
                }
            }
        },
        400: {
            "description": "Bad Request - Invalid price range.",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Invalid minimum or maximum price."
                    }
                }
            }
        }
    }
)
async def list_items(request: Request, min: Optional[int] = None, max: Optional[int] = None):
    async with get_db() as db:
        if min or max is not None:
            product_list = await ProductCrudOperations(db).list_product_min(min, max)
            _list = []
            for i in range(len(product_list)):
                async with get_db() as db:
                    product_gallery = await ProductCrudOperations(db).get_product_gallery_info(product_list[i].product_id)
                _product = ItemBaseOut(
                    item_name=product_list[i].product_name,
                    product_id=product_list[i].product_id,
                    product_price=product_list[i].product_price,
                    product_description=product_list[i].product_description,
                    product_cattegory=product_list[i].product_cattegory,
                    product_stock=product_list[i].product_stock,
                    gallery_items=product_gallery
                )
                _list.append(_product)
        else:
            async with get_db() as db:
                product_list = await ProductCrudOperations(db).list_product()
                _list = []
                for i in range(len(product_list)):
                    async with get_db() as db:
                        product_gallery = await ProductCrudOperations(db).get_product_gallery_info(product_list[i].product_id)
                    _product = ItemBaseOut(
                        item_name=product_list[i].product_name,
                        product_id=product_list[i].product_id,
                        product_price=product_list[i].product_price,
                        product_description=product_list[i].product_description,
                        product_cattegory=product_list[i].product_cattegory,
                        product_stock=product_list[i].product_stock,
                        gallery_items=product_gallery
                    )
                    _list.append(_product)

    return JSONResponse(content=[item.dict() for item in _list])


@router.get(
    "/get_product",
    response_class=JSONResponse,
    response_model=ItemBaseOut,
    tags=["Product Management"],
    description="Retrieves a specific product by its ID.",
    responses={
        200: {
            "description": "Product retrieved successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "item_name": "Sample Product",
                        "product_id": 1,
                        "product_description": "A great product.",
                        "product_stock": 50,
                        "product_cattegory": "Category1",
                        "product_price": 100.0,
                        "gallery_items": []
                    }
                }
            }
        },
        404: {
            "description": "Product not found.",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Product not found"
                    }
                }
            }
        }
    }
)
async def get_product(request: Request, product_id: int):
    async with get_db() as db:
        product_gallery = await ProductCrudOperations(db).get_product_gallery_info(product_id)
    async with get_db() as db:
        product_list = await ProductCrudOperations(db).get_product(product_id)
        _product = ItemBaseOut(
            item_name=product_list.product_name,
            product_id=product_list.product_id,
            product_description=product_list.product_description,
            product_stock=product_list.product_stock,
            product_cattegory=product_list.product_cattegory,
            product_price=product_list.product_price,
            gallery_items=product_gallery
        )

    return _product


@router.get(
    "/list_cattegory",
    response_class=JSONResponse,
    tags=["Product Management"],
    description="Retrieves a list of categories or products within a specified category.",
    responses={
        200: {
            "description": "List of categories or products retrieved successfully.",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "cattegory": "Category1"
                        }
                    ]
                }
            }
        },
        404: {
            "description": "Category not found.",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Category not found"
                    }
                }
            }
        }
    }
)
async def list_cattegory(request: Request, cattegory: Optional[str] = None):
    async with get_db() as db:
        if cattegory is not None:
            product_list = await ProductCrudOperations(db).list_product_cattegory(cattegory)
            _list = []
            for i in range(len(product_list)):
                async with get_db() as db:
                    product_gallery = await ProductCrudOperations(db).get_product_gallery_info(product_list[i].product_id)
                _product = ItemBaseOut(
                    item_name=product_list[i].product_name,
                    product_id=product_list[i].product_id,
                    product_price=product_list[i].product_price,
                    product_description=product_list[i].product_description,
                    product_cattegory=product_list[i].product_cattegory,
                    product_stock=product_list[i].product_stock,
                    gallery_items=product_gallery
                )
                _list.append(_product)

            return JSONResponse(content=[item.dict() for item in _list])
        else:
            async with get_db() as db:
                result = await db.execute(select(Product.product_cattegory).limit(99999999))
                cattegories = result.scalars().all()
                _list = []
                for i in range(len(cattegories)):
                    cattegories_ = CattegoriesOut(
                        cattegory=cattegories[i]
                    )
                    _list.append(cattegories_)
                return JSONResponse(content=[item.dict() for item in _list])


@router.get(
    "/get_product_photos/{gallery_id}",
    description="This Route Returns a Specific Gallery Item",
    tags=["Product Management"],
    responses={
        200: {
            "description": "Gallery item retrieved successfully."
        },
        404: {
            "description": "Gallery item not found.",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Gallery item not found"
                    }
                }
            }
        },
        400: {
            "description": "Unsupported media type.",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Unsupported media type"
                    }
                }
            },
        },
        500: {
            "description": "Internal Server Error.",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Error: <error details>"
                    }
                }
            }
        }
    }
)
async def get_gallery_item(gallery_id: int):
    try:
        async with get_db() as db:
            gallery_item = await ProductCrudOperations(db).get_gallery_item(gallery_id)

        if not gallery_item:
            raise HTTPException(status_code=404, detail="Gallery item not found")

        products_dir = "products"
        product_dir = os.path.join(products_dir, str(gallery_item.product_id))
        file_path = os.path.join(product_dir, os.path.basename(gallery_item.product_image))

        if os.path.exists(file_path):
            if gallery_item.product_image_extension == 'webp':
                media_type = 'image/webp'
            elif gallery_item.product_image_extension == 'mp4':
                media_type = 'video/mp4'
            else:
                raise HTTPException(status_code=400, detail="Unsupported media type")

            return FileResponse(file_path, media_type=media_type)

        else:
            raise HTTPException(status_code=404, detail="File not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

