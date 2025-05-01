from fastapi import Form
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import List, Optional

class ItemBaseOut(BaseModel):
    item_name: str
    product_description: Optional[str]
    product_price:float
    product_id: int
    product_cattegory: Optional[str]
    product_stock: Optional[int]
    gallery_items: Optional[List[dict]] = []  # Galeri öğeleri için opsiyonel liste

class CattegoriesOut(BaseModel):
    cattegory: Optional[str]


class ItemTitleOut(BaseModel):
    item_name: str
    product_photo: str
    product_description: Optional[str]
    product_price:float
    product_id: int
    product_cattegory: Optional[str]

class ListOrderOut(BaseModel):
    order_id: Optional[int] = None
    order: Optional[List[dict]]= None
    address: Optional[str]= None
    tax_id: Optional[str]= None
    phone_number: Optional[str]= None
    basket_price: Optional[float]= None
    order_price: Optional[float]= None
    coupon_code: Optional[str]= None
    order_date: Optional[str]= None
    cargo_id:Optional[str]= None
    user_id: Optional[str]= None

class PaymentStatusOut(BaseModel):
    status:str

class PaymentInputScheme(BaseModel):
    user_id: str

class ItemChangesOut(BaseModel):
    status:Optional[str]

class LoginOutput(BaseModel):
    name: str
    surname: str
    access_token: str
    status: str

class EcommerceBase(BaseModel):
    order_id: int
    order: str
    address: str
    tax_id: str
    phone_number: str
    basket_price: float
    order_price: float
    coupon_code: str
    order_date: datetime
    cargo_id:str
    user_id: UUID


class EcommerceCreate(EcommerceBase):
    pass

class Ecommerce(EcommerceBase):
    class Config:
        orm_mode = True

class ProductBase(BaseModel):
    product_id: int
    product_photo: str
    product_description: str
    product_price: float

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    class Config:
        orm_mode = True

class BasketAdd(BaseModel):
    basket_id:int
    product_id: int
    product_pcs: int
    
    user_id: UUID


class ProductInput(BaseModel):
    product_id: int
    product_name: str
    product_description: str
    product_cattegory: str
    product_price: float
    product_stock: int

    @classmethod
    def as_form(
        cls,
        product_id: int = Form(...),
        product_name: str = Form(...),
        product_description: str = Form(...),
        product_cattegory: str = Form(...),
        product_price: float = Form(...),
        product_stock: int = Form(...)
    ):
        return cls(
            product_id=product_id,
            product_name=product_name,
            product_description=product_description,
            product_cattegory=product_cattegory,
            product_price=product_price,
            product_stock=product_stock
        )
class ProductOut(BaseModel):
    status:str


class GalleryItemUpdate(BaseModel):
    gallery_id: Optional[int]  # Mevcut öğeyi güncellemek için
    product_image_tier: Optional[int]
    product_image_extension: Optional[str]
    product_image: Optional[str]

class ProductUpdate(BaseModel):
    product_name: Optional[str]
    product_photo: Optional[str]
    product_description: Optional[str]
    product_cattegory: Optional[str]
    product_price: Optional[float]
    product_stock: Optional[int]
    gallery_items: Optional[List[GalleryItemUpdate]]  # Galeri öğeleri

class ProductGalleryUpdate(BaseModel):
    gallery_id: Optional[int]  # Galeri öğesinin ID'si
    product_image_tier: Optional[int]  # Tier bilgisi
    product_image_extension: Optional[str]  # Dosya uzantısı
    product_image: Optional[str]  # Yeni resim yolu

class BasketOut(BaseModel):
    product_id:int
    product_name:str
    product_pcs:int
    product_price:float

class OpenToken(BaseModel):
    token: str
    status: bool
    user_id: UUID

class OpenFoil(BaseModel):

    order_id: str
    status: str 
    user_id: UUID
