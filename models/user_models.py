import json
from typing import Optional
from sqlalchemy import Boolean, Integer, String, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from uuid import UUID, uuid4
from datetime import datetime

from db.database import Base


class User(Base):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String, nullable=False)
    surname: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    hashed_pwd: Mapped[str] = mapped_column(String, nullable=False)
    
    tax_id: Mapped[Optional[str]] = mapped_column(String, nullable=True,default="")
    role: Mapped[Optional[str]] = mapped_column(String, nullable=True,default="musteri")
    credit: Mapped[float] = mapped_column(Float, default=0.0)
    reg_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow())
    phone_number: Mapped[Optional[str]] = mapped_column(String, nullable=True,default="")
    verified: Mapped[bool] = mapped_column(Boolean, nullable=False,default=False)
    address1: Mapped[str] = mapped_column(String, nullable=True,default=None)
    address2: Mapped[str] = mapped_column(String, nullable=True,default=None)
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4())

class UserOtp(Base):
    __tablename__ = "otp"

    otp: Mapped[int] = mapped_column(Integer, nullable=True,default=None)
    user_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4())

class ListOfListsEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, list):
            return obj
        return super().default(obj)

class Info(Base):
    __tablename__ = "info"

    language: Mapped[str] = mapped_column(String, primary_key=True)
    about_us: Mapped[str] = mapped_column(String, nullable=True, default=None)
    info: Mapped[str] = mapped_column(String, nullable=True, default=None)
    change_and_refund: Mapped[str] = mapped_column(String, nullable=True, default=None)
    distance_sales_agreement: Mapped[str] = mapped_column(String, nullable=True, default=None)
    privacy_policy: Mapped[str] = mapped_column(String, nullable=True, default=None)

    @classmethod
    def from_dict(cls, language, about_us, info, change_and_refund, distance_sales_agreement, privacy_policy):
        return cls(
            language=language,
            about_us=json.dumps(about_us, cls=ListOfListsEncoder) if about_us is not None else "[]",
            info=json.dumps(info, cls=ListOfListsEncoder) if info is not None else "[]",
            change_and_refund=json.dumps(change_and_refund, cls=ListOfListsEncoder) if change_and_refund is not None else "[]",
            distance_sales_agreement=json.dumps(distance_sales_agreement, cls=ListOfListsEncoder) if distance_sales_agreement is not None else "[]",
            privacy_policy=json.dumps(privacy_policy, cls=ListOfListsEncoder) if privacy_policy is not None else "[]"
        )

    def to_dict(self):
        return {
            "language": self.language,
            "about_us": json.loads(self.about_us) if self.about_us else None,
            "info": json.loads(self.info) if self.info else None,
            "change_and_refund": json.loads(self.change_and_refund) if self.change_and_refund else None,
            "distance_sales_agreement": json.loads(self.distance_sales_agreement) if self.distance_sales_agreement else None,
            "privacy_policy": json.loads(self.privacy_policy) if self.privacy_policy else None
        }