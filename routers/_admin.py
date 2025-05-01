
import json
import os
from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy import select

from crud.product_crud_operations import ProductCrudOperations
from crud.user_crud_operations import UserCrudOperations
from db.database import get_db
from models.product_model import ProductGallery
from models.user_models import Info
from schemas.product_schemas import  ListOrderOut, ProductGalleryUpdate, ProductInput, ProductOut
from schemas.user_schemas import InfoOut, UserListOut, UserOut, UserUpdate
from PIL import Image
import io

from security.security_funcs import  get_current_user_role

router = APIRouter()

@router.post(
    "/admin/add_product",
    response_model=ProductOut,
    response_class=JSONResponse,
    description="This route adds a new product to the database.",
    tags=["Website Admin"],
    responses={
        200: {
            "description": "Product added successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "status": "product_added"
                    }
                }
            }
        },
        401: {
            "description": "UNAUTHORIZED - Not authorized to add products.",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error, Not Auth"
                    }
                }
            }
        },
        400: {
            "description": "BAD REQUEST - Invalid product data.",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error, {error_message}"
                    }
                }
            }
        },
        500: {
            "description": "INTERNAL SERVER ERROR - An unexpected error occurred.",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error, {error_message}"
                    }
                }
            }
        }
    }
)
async def product_add(
    product_id: int = Form(...),
    product_name: str = Form(...),
    product_description: str = Form(...),
    product_cattegory: str = Form(...),
    product_price: float = Form(...),
    product_stock: int = Form(...),
    gallery_files: List[UploadFile] = File(...),
    user: str = Depends(get_current_user_role)
):
    product_input = ProductInput(
        product_id=product_id,
        product_name=product_name,
        product_description=product_description,
        product_cattegory=product_cattegory,
        product_price=product_price,
        product_stock=product_stock
    )

    try:
        async with get_db() as db:
            print(user)
            if user == "admin":
                await ProductCrudOperations(db).create_product(product_input, gallery_files)
            else:
                return ProductOut(status="error, Not Auth")
    except Exception as e:
        print("Exception", e)
        return ProductOut(status=f"error, {e}")

    return ProductOut(status="product_added")



@router.get(
    "/admin/list_orders",
    response_class=JSONResponse,
    response_model=List[ListOrderOut],
    description="This route lists all orders for the admin.",
    tags=["Website Admin"],
    responses={
        200: {
            "description": "Orders listed successfully.",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "order_id": 1,
                            "order": "Order details here",
                            "address": "123 Main St",
                            "tax_id": "123456789",
                            "phone_number": "555-1234",
                            "basket_price": 100.00,
                            "order_price": 120.00,
                            "coupon_code": "SAVE20",
                            "order_date": "2024-01-01T12:00:00",
                            "user_id": "abc123"
                        }
                    ]
                }
            }
        },
        401: {
            "description": "UNAUTHORIZED - Not authorized to list orders.",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error, Not Auth"
                    }
                }
            }
        },
        500: {
            "description": "INTERNAL SERVER ERROR - An unexpected error occurred.",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error, {error_message}"
                    }
                }
            }
        }
    }
)
async def list_items(request: Request, user: str = Depends(get_current_user_role)):
    async with get_db() as db:
        order_list = await ProductCrudOperations(db).list_orders()
        _list = []
        for order in order_list:
            _orders = ListOrderOut(
                order_id=order.order_id,
                order=json.loads(order.order),
                address=order.address,
                tax_id=order.tax_id,
                phone_number=order.phone_number,
                basket_price=order.basket_price,
                order_price=order.order_price,
                coupon_code=order.coupon_code,
                order_date=order.order_date.strftime("%Y-%m-%d %H:%M:%S"),
                user_id=str(order.user_id)
            )
            _list.append(_orders)

    if user == "admin":
        return JSONResponse(content=[item.dict() for item in _list])
    else:
        return ProductOut(status="error, Not Auth")

@router.get(
    "/admin/list_users",
    response_class=JSONResponse,
    response_model=List[UserListOut],
    description="This route lists all users for the admin.",
    tags=["Website Admin"],
    responses={
        200: {
            "description": "Users listed successfully.",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "name": "John",
                            "surname": "Doe",
                            "email": "john.doe@example.com",
                            "hashed_pwd": "hashedpassword123",
                            "tax_id": "123456789",
                            "role": "user",
                            "credit": 100.00,
                            "reg_date": "2024-01-01T12:00:00",
                            "phone_number": "555-1234",
                            "verified": True,
                            "address1": "123 Main St",
                            "address2": "Apt 1B",
                            "id": "abc123"
                        }
                    ]
                }
            }
        },
        401: {
            "description": "UNAUTHORIZED - Not authorized to list users.",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error, Not Auth"
                    }
                }
            }
        },
        500: {
            "description": "INTERNAL SERVER ERROR - An unexpected error occurred.",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error, {error_message}"
                    }
                }
            }
        }
    }
)
async def list_users(request: Request, user_: str = Depends(get_current_user_role)):
    async with get_db() as db:
        user_list = await UserCrudOperations(db).get_users()
        _list = []
        for user in user_list:
            _users = UserListOut(
                name=user.name,
                surname=user.surname,
                email=user.email,
                hashed_pwd=user.hashed_pwd,
                tax_id=user.tax_id,
                role=user.role,
                credit=user.credit,
                reg_date=user.reg_date.isoformat(),
                phone_number=user.phone_number,
                verified=user.verified,
                address1=user.address1,
                address2=user.address2,
                id=str(user.id),
            )
            _list.append(_users)
            
    if user_ == "admin":
        return JSONResponse(content=[item.dict() for item in _list])
    else:
        raise HTTPException(status_code=401,detail="Error Not Auth")


@router.delete(
    "/admin/delete_product/{product_id}",
    response_model=ProductOut,
    description="Delete a product and its gallery items.",
    tags=["Website Admin"],
    responses={
        200: {
            "description": "Product deleted successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "status": "product_deleted"
                    }
                }
            }
        },
        404: {
            "description": "PRODUCT NOT FOUND - The specified product does not exist.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Product not found"
                    }
                }
            }
        },
        401: {
            "description": "UNAUTHORIZED - Not authorized to delete products.",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error, Not Auth"
                    }
                }
            }
        },
        500: {
            "description": "INTERNAL SERVER ERROR - An unexpected error occurred.",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error, {error_message}"
                    }
                }
            }
        }
    }
)
async def delete_product(product_id: int, user: str = Depends(get_current_user_role)):
    if user == "admin":
        async with get_db() as db:
            # Ürünü veritabanından bul
            product = await ProductCrudOperations(db).get_product(product_id)

            if not product:
                raise HTTPException(status_code=404, detail="Product not found")

            # Ürün klasörünü bul
            product_dir = os.path.join("products", str(product_id))
            await db.delete(product)
            await db.commit()

        async with get_db() as db:
            gallery_items = await ProductCrudOperations(db).get_gallery(product_id)

            for gallery_item in gallery_items:
                # Dosyayı sil
                if os.path.exists(gallery_item.product_image):
                    os.remove(gallery_item.product_image)
                await db.delete(gallery_item)
                await db.commit()

            # Ürün klasörünü sil
            if os.path.exists(product_dir):
                os.rmdir(product_dir)

        return ProductOut(status="product_deleted")
    else:
        return ProductOut(status="error, Not Auth")

    
@router.put(
    "/admin/update_product/{product_id}",
    response_model=ProductOut,
    description="Update a product's details and gallery items.",
    tags=["Website Admin"],
    responses={
        200: {
            "description": "Product updated successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "status": "product_updated"
                    }
                }
            }
        },
        404: {
            "description": "PRODUCT NOT FOUND - The specified product does not exist.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Product not found"
                    }
                }
            }
        },
        401: {
            "description": "UNAUTHORIZED - Not authorized to update products.",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error, Not Auth"
                    }
                }
            }
        },
        500: {
            "description": "INTERNAL SERVER ERROR - An unexpected error occurred.",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error, {error_message}"
                    }
                }
            }
        }
    }
)
async def update_product(
    product_id: int,
    product_name: Optional[str] = Form(None),
    product_description: Optional[str] = Form(None),
    product_cattegory: Optional[str] = Form(None),
    product_price: Optional[float] = Form(None),
    product_stock: Optional[int] = Form(None),
    gallery_files: Optional[List[UploadFile]] = File(None),
    gallery_items: Optional[List[ProductGalleryUpdate]] = None,
    gallery_items_to_delete: Optional[List[int]] = None,
    user: str = Depends(get_current_user_role)
):
    if user == "admin":
        async with get_db() as db:
            # Ürünü veritabanından bul
            product = await ProductCrudOperations(db).get_product(product_id)

            if not product:
                raise HTTPException(status_code=404, detail="Product not found")

            # Ürün güncellemeleri
            if product_name is not None:
                product.product_name = product_name
            if product_description is not None:
                product.product_description = product_description
            if product_cattegory is not None:
                product.product_cattegory = product_cattegory
            if product_price is not None:
                product.product_price = product_price
            if product_stock is not None:
                product.product_stock = product_stock

            # Ürünü güncelle ve veritabanına kaydet
            db.add(product)
            await db.commit()
            await db.refresh(product)

        # Galeri güncellemeleri
        if gallery_files:  # Eğer dosya listesi boş değilse
            async with get_db() as db:
                tier = await ProductCrudOperations(db).get_product_gallery_info(product_id)
                tier = len(tier) + 1  # Mevcut galeri öğelerinin sayısından başla
            for file in gallery_files:
                file_content = await file.read()
                file_ext = os.path.splitext(file.filename)[1].lower()

                if file_ext in ['.jpg', '.jpeg', '.png', '.webp']:  # Fotoğraf dosyaları
                    image = Image.open(io.BytesIO(file_content))

                    # Fotoğrafın yeni ismi ve konumu
                    new_filename = f"product_image_{product_id}_{uuid.uuid4().hex}.webp"
                    file_location = os.path.join("products", str(product_id), new_filename)

                    # WebP formatında kaydetme
                    image.save(file_location, format='WEBP')

                    async with get_db() as db:
                        gallery_id = await ProductCrudOperations(db).get_last_gallery()
                        if gallery_id is None:
                            gallery_id = 0

                        # Galeriye fotoğraf ekleme
                        product_gallery = ProductGallery(
                            gallery_id=int(gallery_id) + 1,
                            product_id=product_id,
                            product_image_tier=tier,
                            product_image_extension='webp',
                            product_image=file_location
                        )
                        db.add(product_gallery)
                        await db.commit()
                        await db.refresh(product_gallery)

                elif file_ext in ['.mp4', '.mov', '.avi']:  # Video dosyaları
                    # Videonun yeni ismi ve konumu
                    new_filename = f"product_video_{product_id}_{uuid.uuid4().hex}.mp4"
                    file_location = os.path.join("products", str(product_id), new_filename)

                    # MP4 formatında kaydetme
                    with open(file_location, 'wb') as f:
                        f.write(file_content)

                    async with get_db() as db:
                        gallery_id = await ProductCrudOperations(db).get_last_gallery()
                        if gallery_id is None:
                            gallery_id = 0

                        # Galeriye video ekleme
                        product_gallery = ProductGallery(
                            gallery_id=int(gallery_id) + 1,
                            product_id=product_id,
                            product_image_tier=tier,
                            product_image_extension='mp4',
                            product_image=file_location
                        )
                        db.add(product_gallery)
                        await db.commit()
                        await db.refresh(product_gallery)

                # Her dosya için tier'ı artırıyoruz
                tier += 1

        # Eski galeri öğelerinin silinmesi
        if gallery_items_to_delete:
            for gallery_id in gallery_items_to_delete:
                async with get_db() as db:
                    gallery_item = await ProductCrudOperations(db).get_gallery_item(int(gallery_id))

                    if gallery_item:
                        db.delete(gallery_item)
                        await db.commit()
                        await db.refresh(gallery_item)

        # Eski galeri öğelerinin güncellenmesi
        if gallery_items is not None:
            for item in gallery_items:
                if item.gallery_id:  # Eğer gallery_id mevcutsa güncelle
                    async with get_db() as db:
                        gallery_item = await ProductCrudOperations(db).get_gallery_item(item.gallery_id)

                        if gallery_item:
                            if item.product_image_tier is not None:
                                gallery_item.product_image_tier = item.product_image_tier
                            if item.product_image_extension is not None:
                                gallery_item.product_image_extension = item.product_image_extension
                            if item.product_image is not None:
                                gallery_item.product_image = item.product_image
                        else:
                            raise HTTPException(status_code=404, detail=f"Gallery item with id {item.gallery_id} not found")

        # Tiers güncellemesi
        async with get_db() as db:
            await ProductCrudOperations(db).update_gallery_tiers(product_id)

        return ProductOut(status="product_updated")
    else:
        return ProductOut(status="error, Not Auth")

@router.put(
    "/admin/edit_order/{order_id}",
    response_class=JSONResponse,
    response_model=ListOrderOut,
    description="This Route For Editing Orders.",
    tags=["Website Admin"],
    responses={
        200: {
            "description": "Order updated successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "order_id": 1,
                        "order": "New order details",
                        "address": "New address",
                        "tax_id": "New tax ID",
                        "phone_number": "New phone number",
                        "basket_price": 100.0,
                        "order_price": 120.0,
                        "coupon_code": "NEWCOUPON",
                        "order_date": "2024-10-15T10:00:00",
                        "user_id": "123456"
                    }
                }
            }
        },
        404: {
            "description": "ORDER NOT FOUND - The specified order does not exist.",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Order not found"
                    }
                }
            }
        },
        401: {
            "description": "UNAUTHORIZED - Not authorized to edit orders.",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error, Not Auth"
                    }
                }
            }
        },
        500: {
            "description": "INTERNAL SERVER ERROR - An unexpected error occurred.",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error, {error_message}"
                    }
                }
            }
        }
    }
)
async def edit_order(
    request: Request,
    order_id: int,
    order_data: ListOrderOut,
    user: str = Depends(get_current_user_role)
):
    if user == "admin":
        async with get_db() as db:
            # Siparişi güncellemek için update_order fonksiyonunu çağırıyoruz
            updated_order = await ProductCrudOperations(db).update_order(order_id=order_id, scheme=order_data)

            # Eğer sipariş bulunamazsa 404 döndürülür
            if not updated_order:
                return JSONResponse(status_code=404, content={"message": "Order not found"})

            # Güncellenen siparişin verilerini JSON olarak döndür
            return JSONResponse(content=updated_order.dict())
    else:
        return JSONResponse(content={"status": "error, Not Auth"}, status_code=401)

@router.put(
    "/admin/edit_user/{user_id}",
    response_class=JSONResponse,
    response_model=UserOut,
    description="This Route For Editing Users.",
    tags=["Website Admin"],
    responses={
        200: {
            "description": "User updated successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "name": "John",
                        "surname": "Doe",
                        "email": "john.doe@example.com",
                        "tax_id": "123456789",
                        "role": "admin",
                        "credit": 100.0,
                        "reg_date": "2024-10-15T10:00:00",
                        "phone_number": "555-1234",
                        "verified": True,
                        "address1": "123 Main St",
                        "address2": "Apt 4B",
                        "id": "1"
                    }
                }
            }
        },
        404: {
            "description": "USER NOT FOUND - The specified user does not exist.",
            "content": {
                "application/json": {
                    "example": {
                        "message": "User not found"
                    }
                }
            }
        },
        403: {
            "description": "FORBIDDEN - Not authorized to edit users.",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Not Authorized"
                    }
                }
            }
        },
        500: {
            "description": "INTERNAL SERVER ERROR - An unexpected error occurred.",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error, {error_message}"
                    }
                }
            }
        }
    }
)
async def edit_user(
    request: Request,
    user_id: str,
    user_data: UserUpdate,
    user: str = Depends(get_current_user_role)
):
    if user == "admin":
        async with get_db() as db:
            # Kullanıcıyı güncellemek için update_user fonksiyonunu çağırıyoruz
            updated_user = await UserCrudOperations(db).update_user(user_id, user_data)

            # Eğer kullanıcı bulunamazsa 404 döndürülür
            if not updated_user:
                return JSONResponse(status_code=404, content={"message": "User not found"})

            # Güncellenen kullanıcının verilerini JSON olarak döndür
            return updated_user
    else:
        return JSONResponse(status_code=403, content={"message": "Not Authorized"})


@router.get(
    "/info",
    response_class=JSONResponse,
    response_model=List[InfoOut],
    tags=["Info"],
    responses={
        200: {
            "description": "Successfully retrieved information.",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "language": "en",
                            "about_us": {
                                "description": "About us in English.",
                                "images": ["url1", "url2"]
                            },
                            "contact": {
                                "email": "info@example.com",
                                "images": ["url3"]
                            },
                            "change_and_refund": {
                                "policy": "Refund policy details.",
                                "images": ["url4"]
                            },
                            "distance_sales_agreement": {
                                "agreement": "Distance sales agreement details.",
                                "images": ["url5"]
                            },
                            "privacy_policy": {
                                "policy": "Privacy policy details.",
                                "images": ["url6"]
                            }
                        }
                    ]
                }
            }
        },
        500: {
            "description": "INTERNAL SERVER ERROR - An unexpected error occurred.",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error, {error_message}"
                    }
                }
            }
        }
    }
)
async def list_info(request: Request):
    async with get_db() as db:
        try:
            result = await db.execute(select(Info).limit(99999999))
            info_list = result.scalars().all()
            _list = []
            for info_item in info_list:
                info__ = {
                    "language": info_item.language,
                    "about_us": {
                        "description": json.loads(info_item.about_us)["description"] if info_item.about_us else None,
                        "images": [f"/get_info_item/{image_id}" for image_id in json.loads(info_item.about_us).get("images", [])]
                    },
                    "contact": {
                        "email": json.loads(info_item.info)["email"] if info_item.info else None,
                        "images": [f"/get_info_item/{image_id}" for image_id in json.loads(info_item.info).get("images", [])]
                    },
                    "change_and_refund": {
                        "policy": json.loads(info_item.change_and_refund)["policy"] if info_item.change_and_refund else None,
                        "images": [f"/get_info_item/{image_id}" for image_id in json.loads(info_item.change_and_refund).get("images", [])]
                    },
                    "distance_sales_agreement": {
                        "agreement": json.loads(info_item.distance_sales_agreement)["agreement"] if info_item.distance_sales_agreement else None,
                        "images": [f"/get_info_item/{image_id}" for image_id in json.loads(info_item.distance_sales_agreement).get("images", [])]
                    },
                    "privacy_policy": {
                        "policy": json.loads(info_item.privacy_policy)["policy"] if info_item.privacy_policy else None,
                        "images": [f"/get_info_item/{image_id}" for image_id in json.loads(info_item.privacy_policy).get("images", [])]
                    }
                }
                _list.append(info__)
            return JSONResponse(content=_list)
        except Exception as e:
            return JSONResponse(status_code=500, content={"status": f"error, {str(e)}"})


@router.put(
    "/admin/edit_info",
    response_class=JSONResponse,
    response_model=InfoOut,
    description="This Route For Editing And Adding Infos",
    tags=["Website Admin"],
    responses={
        200: {
            "description": "Successfully updated or added information.",
            "content": {
                "application/json": {
                    "example": {
                        "language": "en",
                        "about_us": [{"description": "Updated about us content.", "images": ["url1", "url2"]}],
                        "contact": [{"email": "info@example.com", "images": ["url3"]}],
                        "change_and_refund": [{"policy": "Updated refund policy.", "images": ["url4"]}],
                        "distance_sales_agreement": [{"agreement": "Updated distance sales agreement.", "images": ["url5"]}],
                        "privacy_policy": [{"policy": "Updated privacy policy.", "images": ["url6"]}]
                    }
                }
            }
        },
        403: {
            "description": "FORBIDDEN - Not Authorized to edit info.",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Not Authorized"
                    }
                }
            }
        },
        500: {
            "description": "INTERNAL SERVER ERROR - An unexpected error occurred.",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error, {error_message}"
                    }
                }
            }
        }
    }
)
async def edit_info(
    request: Request,
    scheme: InfoOut,
    user: str = Depends(get_current_user_role),
    about_us_files: Optional[List[UploadFile]] = File(None),
    contact_files: Optional[List[UploadFile]] = File(None),
    change_and_refund_files: Optional[List[UploadFile]] = File(None),
    distance_sales_agreement_files: Optional[List[UploadFile]] = File(None),
    privacy_policy_files: Optional[List[UploadFile]] = File(None),
    about_us_images_to_delete: Optional[List[int]] = None,
    contact_images_to_delete: Optional[List[int]] = None,
    change_and_refund_images_to_delete: Optional[List[int]] = None,
    distance_sales_agreement_images_to_delete: Optional[List[int]] = None,
    privacy_policy_images_to_delete: Optional[List[int]] = None,
):
    if user == "admin":
        try:
            async with get_db() as db:
                # Fotoğrafları kaydetme fonksiyonu
                def save_image(file: UploadFile, image_id: int):
                    file_content = file.read()
                    image = Image.open(io.BytesIO(file_content))
                    file_location = f"images/{image_id}.webp"  # ID ile kaydet
                    image.save(file_location, format='WEBP')
                    return file_location

                # Yeni fotoğraflar için ID'leri kaydet
                if about_us_files:
                    for file in about_us_files:
                        image_id = len(scheme.about_us[0]["images"]) + 1  # Yeni ID belirle
                        file_location = save_image(file, image_id)
                        scheme.about_us[0]["images"].append(file_location)

                if contact_files:
                    for file in contact_files:
                        image_id = len(scheme.contact[0]["images"]) + 1  # Yeni ID belirle
                        file_location = save_image(file, image_id)
                        scheme.contact[0]["images"].append(file_location)

                if change_and_refund_files:
                    for file in change_and_refund_files:
                        image_id = len(scheme.change_and_refund[0]["images"]) + 1  # Yeni ID belirle
                        file_location = save_image(file, image_id)
                        scheme.change_and_refund[0]["images"].append(file_location)

                if distance_sales_agreement_files:
                    for file in distance_sales_agreement_files:
                        image_id = len(scheme.distance_sales_agreement[0]["images"]) + 1  # Yeni ID belirle
                        file_location = save_image(file, image_id)
                        scheme.distance_sales_agreement[0]["images"].append(file_location)

                if privacy_policy_files:
                    for file in privacy_policy_files:
                        image_id = len(scheme.privacy_policy[0]["images"]) + 1  # Yeni ID belirle
                        file_location = save_image(file, image_id)
                        scheme.privacy_policy[0]["images"].append(file_location)

                # Fotoğrafları silme işlemleri
                async def delete_images(image_ids):
                    for image_id in image_ids:
                        # Veritabanından resmi bul ve sil
                        # Silme işlemi, örneğin db.delete ile yapılabilir
                        await ProductCrudOperations(db).delete_image(image_id)

                if about_us_images_to_delete:
                    await delete_images(about_us_images_to_delete)

                if contact_images_to_delete:
                    await delete_images(contact_images_to_delete)

                if change_and_refund_images_to_delete:
                    await delete_images(change_and_refund_images_to_delete)

                if distance_sales_agreement_images_to_delete:
                    await delete_images(distance_sales_agreement_images_to_delete)

                if privacy_policy_images_to_delete:
                    await delete_images(privacy_policy_images_to_delete)

                # Güncellenmiş bilgileri veritabanında güncelle
                updated_info = await UserCrudOperations(db).update_info(scheme)
                return JSONResponse(content=updated_info.dict())
        except Exception as e:
            return JSONResponse(status_code=500, content={"status": f"error, {str(e)}"})
    else:
        return JSONResponse(status_code=403, content={"message": "Not Authorized"})


@router.get("/get_info_item/{image_id}", response_class=FileResponse,tags=["Info"])
async def get_info_item(image_id: int):
    """
    Get an image by its ID from the images directory.

    Parameters:
    - image_id (int): The ID of the image to retrieve.

    Returns:
    - FileResponse: The image file in .webp format if found.

    Raises:
    - HTTPException: If the image is not found, a 404 error is raised.
    - HTTPException: If an unexpected error occurs, a 500 error is raised.
    """
    try:
        # Dosya yolunu tanımla
        file_path = f"images/{image_id}.webp"  # ID ile dosya ismi
       
        # Dosya var mı kontrol et
        if os.path.exists(file_path):
            return FileResponse(file_path, media_type='image/webp')
        else:
            raise HTTPException(status_code=404, detail="File not found")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")