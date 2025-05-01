import hashlib
import json
from typing import Optional
from cachetools import TTLCache
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from hashlib import sha256
from uuid import UUID, uuid4

from db.database import get_db
from models.user_models import Info, User, UserOtp
from schemas.user_schemas import InfoOut, UserCreate, UserUpdate

class UserCrudOperations:
    def __init__(self,db_session:AsyncSession):
        self.db_session = db_session

    async def get_user(self,user_id: str):
        try:
            async with self.db_session as session:
                result = await session.execute(select(User).filter(User.id == UUID(user_id)))
                return result.scalars().first()
        except:
            return None
    
    async def get_user_email(self,user_name: str):
        try:
            async with self.db_session as session:
                result = await session.execute(select(User).filter(User.email == user_name))
                return result.scalars().first()
        except:
            return None

    async def create_user(self, user: UserCreate):
        print("Hİİİİİİİİİİİİİİİ5")
        salted_password = user.password + "5ce716692513a8afbb73ae280a1821deae403f6655774af99c5626e97219cc2d"
        hashed_password = sha256(salted_password.encode("utf-8")).hexdigest()
        db_user = User(
            id=uuid4(),
            name=user.name, 
            surname=user.surname, 
            email=user.email, 
            hashed_pwd=hashed_password, 
            phone_number=user.phone_number
        )
        async with self.db_session as session:
            try:
                session.add(db_user)
                await session.commit()
                await session.refresh(db_user)
                return db_user
            except Exception as e:
                print(e) 
        result = await session.execute(select(User).filter(User.email == user.email))
        return result.scalars().first()
    
    

    async def update_user(
        self,
        user_id: UUID,
        scheme:UserUpdate,
    ):
        user = await self.get_user(user_id)
        if user is None:
            return None 

        updated_fields = False

        # Güncelleme işlemleri
        if scheme.name is not None:
            user.name = scheme.name
            updated_fields = True
        if scheme.surname is not None:
            user.surname = scheme.surname
            updated_fields = True
        if scheme.email is not None:
            user.email = scheme.email
            updated_fields = True
        if scheme.password is not None:
            salted_password = scheme.password + "5ce716692513a8afbb73ae280a1821deae403f6655774af99c5626e97219cc2d"
            user.hashed_pwd = sha256(salted_password.encode("utf-8")).hexdigest()
            updated_fields = True
        if scheme.role is not None:
            user.role = scheme.role
            updated_fields = True
        if scheme.phone_number is not None:
            user.phone_number = scheme.phone_number
            updated_fields = True
        if scheme.tax_id is not None:
            user.tax_id = scheme.tax_id
            updated_fields = True
        if scheme.address1 is not None:
            user.address1 = scheme.address1
            updated_fields = True
        if scheme.address2 is not None:
            user.address2 = scheme.address2
            updated_fields = True

        if updated_fields:  # Sadece değişiklik varsa veritabanını güncelle
            async with self.db_session as session:
                session.add(user)
                await session.commit()
                await session.refresh(user)

        return user

    async def get_users(self):
        async with self.db_session as session:
            result = await session.execute(select(User).limit(99999999))
            return result.scalars().all()
    
    async def update_otp(self, user_id: UUID, otp: int,otp_cache:TTLCache) -> bool:
        # Kullanıcının OTP'sini cache'ten al
        print(otp_cache)
        stored_otp = otp_cache[(user_id)]
        print(stored_otp,"AAAAAAAAAAAAAAAAAAAAAAAAAAAAa")
        # Eğer OTP cache'te yoksa veya kullanıcı bulunamıyorsa, False döndür
        if stored_otp is None:
            return False  # OTP cache'te yok

        # Eğer OTP doğrulanırsa
        if int(stored_otp) == otp:
            print("here")
            # Kullanıcıyı güncellemek için veritabanından al
            async with get_db() as db:
                user = await UserCrudOperations(db).get_user(str(user_id))
                print(user)
                # Eğer kullanıcı bulunamazsa, False döndür
                if not user:
                    return False
                
                # Kullanıcı doğrulanmış mı?
                if not user.verified:
                    user.verified = True
                    async with get_db() as db:
                        db.add(user)
                        await db.commit()  # Değişiklikleri kaydet
                        await db.refresh(user)  # Kullanıcıyı güncel verilerle yenile
                        del otp_cache[user_id]  # Doğrulandıktan sonra OTP'yi cache'ten kaldır
                        return True
                else:
                    return False  # Kullanıcı zaten doğrulanmışsa

        return False  # OTP yanlışsa


    async def update_user_local(
            self,
            user_id: str,
            name: Optional[str] = None,
            surname: Optional[str] = None,
            email: Optional[str] = None,
            password: Optional[str] = None,
            phone_number: Optional[str] = None,
            tax_id: Optional[str] = None,
            address1: Optional[str] = None,
            credit: Optional[str] = None,
            address2: Optional[str] = None,
        ):
            async with self.db_session as session:
                result = await session.execute(select(User).filter(User.id == user_id))
                user = result.scalars().first()
            if user is None:
                return None 

            updated_fields = False

            # Güncelleme işlemleri
            if name is not None:
                user.name = name
                updated_fields = True
            if surname is not None:
                user.surname = surname
                updated_fields = True
            if credit is not None:
                user.credit = credit
                updated_fields = True
            if email is not None:
                user.email = email
                updated_fields = True
            if password is not None:
                salted_password = password + "5ce716692513a8afbb73ae280a1821deae403f6655774af99c5626e97219cc2d"
                user.hashed_pwd = sha256(salted_password.encode("utf-8")).hexdigest()
                updated_fields = True
            if phone_number is not None:
                user.phone_number = phone_number
                updated_fields = True
            if tax_id is not None:
                user.tax_id = tax_id
                updated_fields = True
            if address1 is not None:
                user.address1 = address1
                updated_fields = True
            if address2 is not None:
                user.address2 = address2
                updated_fields = True

            if updated_fields:  # Sadece değişiklik varsa veritabanını güncelle
                async with self.db_session as session:
                    session.add(user)
                    await session.commit()
                    await session.refresh(user)

            return user
    
    async def set_otp(self, user_id: str,otp:int):
        db_user = UserOtp(
            user_id=UUID(user_id), 
            otp=otp, 
        )
        async with self.db_session as session:
            try:
                session.add(db_user)
                await session.commit()
                await session.refresh(db_user)
                return db_user
            except Exception as e:
                print(e) 
        result = await session.execute(select(UserOtp).filter(UserOtp.user_id == UUID(user_id)))
        print("SAAAAAAAAAAAAAAAAAAAAAA")
        return result.scalars().first()
    async def get_info_language(self,language: str):
        try:
            async with self.db_session as session:
                result = await session.execute(select(Info).filter(Info.language == language))
                return result.scalars().first()
        except:
            return None
    
    async def update_info(
            self,
            scheme: InfoOut,
        ):
            updated_fields = False
            info_ = await self.get_info_language(scheme.language)
            if info_ is None:
                updated_fields = True
                info_ = Info(
                    language=scheme.language,
                    about_us=json.dumps(scheme.about_us),
                    info=json.dumps(scheme.contact),
                    change_and_refund=json.dumps(scheme.change_and_refund),
                    distance_sales_agreement=json.dumps(scheme.distance_sales_agreement),
                    privacy_policy=json.dumps(scheme.privacy_policy)
                )

            # Güncelleme işlemleri
            if scheme.about_us is not None:
                info_.about_us = json.dumps(scheme.about_us)
                updated_fields = True
            if scheme.contact is not None:
                info_.info = json.dumps(scheme.contact)
                updated_fields = True
            if scheme.change_and_refund is not None:
                info_.change_and_refund = json.dumps(scheme.change_and_refund)
                updated_fields = True
            if scheme.distance_sales_agreement is not None:
                info_.distance_sales_agreement = json.dumps(scheme.distance_sales_agreement)
                updated_fields = True
            if scheme.privacy_policy is not None:
                info_.privacy_policy = json.dumps(scheme.privacy_policy)
                updated_fields = True

            if updated_fields:  # Sadece değişiklik varsa veritabanını güncelle
                async with self.db_session as session:
                    session.add(info_)
                    await session.commit()
                    await session.refresh(info_)

            # Geri dönerken json.loads ile veriyi uygun formata çevirin
            return {
                "language": info_.language,
                "about_us": json.loads(info_.about_us) if info_.about_us else None,
                "contact": json.loads(info_.info) if info_.info else None,
                "change_and_refund": json.loads(info_.change_and_refund) if info_.change_and_refund else None,
                "distance_sales_agreement": json.loads(info_.distance_sales_agreement) if info_.distance_sales_agreement else None,
                "privacy_policy": json.loads(info_.privacy_policy) if info_.privacy_policy else None,
            }
