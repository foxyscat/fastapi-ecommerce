import json
import os
from typing import List
import uuid
from fastapi import UploadFile
from sqlalchemy import and_
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from crud.user_crud_operations import UserCrudOperations
from db.database import get_db
from models.product_model import Basket, FoilControl, Order, Product, ProductGallery
from models.user_models import User
from schemas.product_schemas import EcommerceBase, ListOrderOut, ProductInput
from PIL import Image
import io

class ProductCrudOperations:
    def __init__(self,db_session:AsyncSession):
        self.db_session = db_session

    async def get_basket(self,product_id: int,user_id: UUID):
        try:
            async with get_db() as session:
                result = await session.execute(
                    select(Basket).filter(
                        and_(Basket.user_id == user_id, Basket.product_id == product_id)
                    )
                )                
                return result.scalars().first()
        except Exception as e:
            print(e,"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
            return None
    
    async def get_basket_all(self,user_id: UUID):
        try:
            async with get_db() as session:
                result = await session.execute(select(Basket).filter(Basket.user_id == user_id))         
                return result.scalars().all()
        except Exception as e:
            print(e,"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
            return None
    
    async def get_product(self,item_id: int):
        try:
            async with self.db_session as session:
                result = await session.execute(select(Product).filter(Product.product_id == item_id))
                return result.scalars().first()
        except Exception as e:
            return None
        
    async def get_last_product(self):
        try:
            async with self.db_session as session:
                    # En son eklenen ürünü getir (id'ye göre sıralayarak)
                # ID'ye göre azalan sırada sırala ve en son eklenen kaydı al
                result = await session.execute(
                    select(Basket.basket_id).order_by(Basket.basket_id.desc()).limit(1)
                )
                return result.scalars().first()  # En son eklenen kaydı döndürür
        except Exception as e:
            print(e)
            return None
        
    async def get_last_gallery(self):
        try:
            async with self.db_session as session:
                    # En son eklenen ürünü getir (id'ye göre sıralayarak)
                # ID'ye göre azalan sırada sırala ve en son eklenen kaydı al
                result = await session.execute(
                    select(ProductGallery.gallery_id).order_by(ProductGallery.gallery_id.desc()).limit(1)
                )
                return result.scalars().first()  # En son eklenen kaydı döndürür
        except Exception as e:
            print(e)
            return None
        
    async def list_product(self):
        try:
            async with self.db_session as session:
                # Select products with a limit based on item_count
                result = await session.execute(select(Product).limit(99999999))
                return result.scalars().all()
        except Exception as e:
            print(e)
            return None
    async def list_orders(self):
        try:
            async with self.db_session as session:
                # Select products with a limit based on item_count
                result = await session.execute(select(Order).limit(99999999))
                return result.scalars().all()
        except Exception as e:
            print(e)
            return None
        
    async def list_orders_user_id(self,user_id:str):
        try:
            async with self.db_session as session:
                # Select products with a limit based on item_count
                result = await session.execute(select(Order).filter(Order.user_id == user_id))
                return result.scalars().all()
        except Exception as e:
            print(e)
            return None    
    async def list_product_cattegory(self, cattegory: str):
        try:
            async with self.db_session as session:
                # Select products with a limit based on item_count
                result = await session.execute(select(Product).filter(Product.product_cattegory == cattegory))
                return result.scalars().all()
        except Exception as e:
            print(e)
            return None
        
    async def list_product_min(self, item_count_min: int, item_count_max: int):
        try:
            async with self.db_session as session:
                # Ürünleri belirli bir aralıkta seç
                result = await session.execute(
                    select(Product).offset(item_count_min).limit(item_count_max - item_count_min)
                )
                return result.scalars().all()
        except Exception as e:
            print(e)
            return None
            
    async def create_order(self, table: EcommerceBase):
        async with get_db() as db:
            user = await UserCrudOperations(db).get_user(str(table.user_id))
            localcredit = user.credit
        order_json = json.loads(table.order)
        for i in range(len(order_json)):
            credit_updated = localcredit+(order_json[i]["product_pcs"]*1000)
            if order_json[i]["product_name"] == "Foil":
                async with get_db() as db:
                    updated_local_user = await UserCrudOperations(db).update_user_local(
                        user_id=table.user_id, credit=credit_updated
                    )
        order = Order(
            order_id=table.order_id,
            order=table.order,
            address=table.address,
            tax_id=table.tax_id,
            phone_number=table.phone_number,
            basket_price=table.basket_price,
            order_price=table.order_price,
            coupon_code=table.coupon_code,
            order_date=table.order_date,
            cargo_id=table.cargo_id,
            user_id=table.user_id
        )
        async with self.db_session as session:
            try:
                session.add(order)
                await session.commit()
                await session.refresh(order)
                return order
            except Exception as e:
                print(e) 

    async def create_product(self, table: ProductInput, gallery_files: List[UploadFile]):
        # Ürün oluşturuluyor
        product = Product(
            product_id=table.product_id,
            product_stock=table.product_stock,
            product_price=table.product_price,
            product_name=table.product_name,
            product_description=table.product_description,
            product_cattegory=table.product_cattegory,
            product_photo=''  # Fotoğraf dosya yolu henüz boş
        )

        # Ürün ID'sine göre klasör oluşturma
        products_dir = "products"
        product_dir = os.path.join(products_dir, str(table.product_id))
        os.makedirs(product_dir, exist_ok=True)

        # Galeri dosyaları kaydetme ve sıralama için tier belirleme
        tier = 1
        for file in gallery_files:
            file_content = await file.read()
            file_ext = os.path.splitext(file.filename)[1].lower()

            if file_ext in ['.jpg', '.jpeg', '.png','.webp']:  # Fotoğraf dosyaları
                image = Image.open(io.BytesIO(file_content))

                # Fotoğrafın yeni ismi ve konumu
                new_filename = f"product_image_{table.product_id}_{uuid.uuid4().hex}.webp"
                file_location = os.path.join(product_dir, new_filename)

                # WebP formatında kaydetme
                image.save(file_location, format='WEBP')
                async with self.db_session as session:
                    gallery_id = await ProductCrudOperations(session).get_last_gallery()
                    if gallery_id == None:
                        gallery_id = 0
                # Galeriye fotoğraf ekleme
                product_gallery = ProductGallery(
                    gallery_id=int(gallery_id)+1,
                    product_id=table.product_id,
                    product_image_tier=tier,  # Sıralama için tier belirleniyor
                    product_image_extension='webp',
                    product_image=file_location
                )
                async with self.db_session as session:
                    session.add(product_gallery)
                    await session.commit()
                    await session.refresh(product_gallery)
            elif file_ext in ['.mp4', '.mov', '.avi']:  # Video dosyaları
                # Videonun yeni ismi ve konumu
                new_filename = f"product_video_{table.product_id}_{uuid.uuid4().hex}.mp4"
                file_location = os.path.join(product_dir, new_filename)

                # MP4 formatında kaydetme
                with open(file_location, 'wb') as f:
                    f.write(file_content)
                async with self.db_session as session:
                    gallery_id = await ProductCrudOperations(session).get_last_gallery()
                    if gallery_id == None:
                        gallery_id = 0
                # Galeriye video ekleme
                product_gallery = ProductGallery(
                    gallery_id=int(gallery_id)+1,
                    product_id=table.product_id,
                    product_image_tier=tier,  # Sıralama için tier belirleniyor
                    product_image_extension='mp4',
                    product_image=file_location
                )
                async with self.db_session as session:
                    session.add(product_gallery)
                    await session.commit()
                    await session.refresh(product_gallery)
            # Her dosya için tier'ı artırıyoruz
            tier += 1

        # Veritabanına kaydetme işlemi
        async with self.db_session as session:
            try:
                session.add(product)
                await session.commit()
                await session.refresh(product)
                return product
            except Exception as e:
                print(e)


    async def empty_basket(self, user_id: str):
        async with self.db_session as session:
            result = await session.execute(select(Basket).filter(Basket.user_id == UUID(user_id)))         
            basket = result.scalars().all()
        
            if basket:
                try:
                    await session.delete(basket)
                    await session.commit()
                    return {"detail": "Basket item deleted successfully"}
                except Exception as e:
                    print(e)

    async def get_gallery(self,product_id):
        async with self.db_session as session:
            gallery_items = await session.execute(select(ProductGallery).where(ProductGallery.product_id == product_id))
            return gallery_items.scalars().all()   
         
    async def get_gallery_item(self,gallery_id):
        async with self.db_session as session:
            gallery_item = await session.execute(select(ProductGallery).where(ProductGallery.gallery_id == gallery_id))
            return  gallery_item.scalar()
        
    async def update_gallery_tiers(self,product_id: int):
        async with self.db_session as session:
            gallery_items = await session.execute(select(ProductGallery).where(ProductGallery.product_id == product_id))
            gallery_items = gallery_items.scalars().all()

            # Sıralama değerini güncelle
            for index, item in enumerate(gallery_items):
                item.product_image_tier = index + 1
            await session.commit()

    async def get_product_gallery_info(self,product_id: int):
        try:
            # Ürün galerisini veritabanından al
            async with self.db_session as session:
                gallery_list = await ProductCrudOperations(session).get_gallery(product_id)

            if not gallery_list:
                return "status_code=404, detail=No gallery items found for this product"

            # Ürün klasöründeki dosyaları kontrol et
            products_dir = "products"
            product_dir = os.path.join(products_dir, str(product_id))
            if not os.path.exists(product_dir):
                return "status_code=404, detail=No gallery items found for this product"

            # Galeri öğelerini JSON formatında döndür
            gallery_json = []
            for gallery_item in gallery_list:
                file_path = os.path.join(product_dir, os.path.basename(gallery_item.product_image))

                if os.path.exists(file_path):
                    # Medya türünü belirle
                    if gallery_item.product_image_extension == 'webp':
                        media_type = 'image/webp'
                    elif gallery_item.product_image_extension == 'mp4':
                        media_type = 'video/mp4'
                    else:
                        return "status_code=404, detail=No gallery items found for this product"

                    # JSON formatında dosya bilgisi ekle
                    gallery_json.append({
                        "product_image_tier": gallery_item.product_image_tier,
                        "media_type": media_type,
                        "file_url": f"/get_product_photos/{gallery_item.gallery_id}"  # Dosyayı indirmek için kullanılacak URL
                    })
                else:
                    return "status_code=404, detail=No gallery items found for this product"

            return gallery_json

        except Exception as e:
                return "status_code=404, detail=No gallery items found for this product"
        
    async def update_order(self, order_id: int, scheme: ListOrderOut):
        async with self.db_session as session:
            # Siparişi ID ile bulma işlemi
            order_item = await session.execute(select(Order).where(Order.order_id == order_id))
            order_item = order_item.scalar()

            # Eğer sipariş bulunamazsa None döndürülür
            if not order_item:
                return None

            # Siparişin alanlarını güncelle
            order_item.order = scheme.order
            order_item.address = scheme.address
            order_item.tax_id = scheme.tax_id
            order_item.phone_number = scheme.phone_number
            order_item.basket_price = scheme.basket_price
            order_item.order_price = scheme.order_price
            order_item.coupon_code = scheme.coupon_code
            order_item.order_date = scheme.order_date
            order_item.user_id = scheme.user_id
            order_item.cargo_id = scheme.cargo_id

            # Değişiklikleri veritabanına yaz
            await session.commit()

            # Güncellenen siparişi geri döndür
            return order_item
        