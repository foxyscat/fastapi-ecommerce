from sqlalchemy import JSON, Boolean, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, MappedAsDataclass
from uuid import UUID, uuid4
from datetime import datetime

from db.database import Base

class Order(Base):
    __tablename__ = "orders"

    order_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order: Mapped[str] = mapped_column(Text, nullable=False)
    address: Mapped[str] = mapped_column(String, nullable=False)
    tax_id: Mapped[str] = mapped_column(String, nullable=False)
    phone_number: Mapped[str] = mapped_column(String, nullable=False)
    basket_price: Mapped[float] = mapped_column(Float, nullable=False)
    order_price: Mapped[float] = mapped_column(Float, nullable=False)
    coupon_code: Mapped[str] = mapped_column(String, nullable=True)
    order_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    cargo_id:Mapped[str] = mapped_column(String, nullable=True)
    user_id: Mapped[UUID] = mapped_column(nullable=False, default=uuid4())

class Product(Base):
    __tablename__ = "product"

    product_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_name: Mapped[str] = mapped_column(String, nullable=False)
    product_photo: Mapped[str] = mapped_column(String, nullable=False)
    product_description: Mapped[str] = mapped_column(String, nullable=False)
    product_cattegory: Mapped[str] = mapped_column(String, nullable=False)
    product_price: Mapped[float] = mapped_column(Float, nullable=False)
    product_stock: Mapped[int] = mapped_column(Integer, nullable=False)

class ProductGallery(Base):
    __tablename__ = "product_gallery"
    gallery_id:Mapped[int] = mapped_column(Integer, primary_key=True,autoincrement=True)
    product_id: Mapped[int] = mapped_column(Integer, nullable=False)
    product_image_tier: Mapped[int] = mapped_column(Integer, nullable=False)
    product_image_extension: Mapped[str] = mapped_column(String, nullable=False)
    product_image: Mapped[str] = mapped_column(String, nullable=False)


class Basket(Base):
    __tablename__ = "basket"
    basket_id:  Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(Integer, nullable=False)
    product_pcs: Mapped[int] = mapped_column(Integer, nullable=False)

    user_id: Mapped[UUID] = mapped_column(nullable=False, default=uuid4())

class CouponCodes(Base):
    __tablename__ = "couponcodes"

    coupon_code: Mapped[str] = mapped_column(String, primary_key=True)
    coupon_discount: Mapped[int] = mapped_column(Integer,nullable=False)
    coupon_var: Mapped[int] = mapped_column(Integer,nullable=False)
    coupon_state: Mapped[bool] = mapped_column(Boolean,nullable=False)



class UserCouponCodes(Base):
    __tablename__ = "usercouponcodes"

    couponcode: Mapped[str] = mapped_column(String, nullable=False,primary_key=True)
    user_id: Mapped[UUID] = mapped_column(nullable=False, default=uuid4())

class Device(Base):
    __tablename__ = "devices"

    device_id: Mapped[str] = mapped_column(String, primary_key=True)
    device_credit: Mapped[float] = mapped_column(Float,nullable=True)
    user_id: Mapped[UUID] = mapped_column(nullable=False, default=uuid4())

class FoilControl(Base):
    __tablename__ = "foilcontrol"

    id:Mapped[int] = mapped_column(Integer, primary_key=True,autoincrement=True)
    order_id: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String,nullable=False)
    user_id: Mapped[UUID] = mapped_column(nullable=False, default=uuid4())


class PaymentToken(Base):
    __tablename__ = "opentokens"

    token: Mapped[str] = mapped_column(String,nullable=False,primary_key=True)
    status: Mapped[bool] = mapped_column(Boolean,nullable=False)
    user_id: Mapped[UUID] = mapped_column(nullable=False, default=uuid4())