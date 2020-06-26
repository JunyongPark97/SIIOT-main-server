import uuid

from django.conf import settings
from django.db.models import Avg
from rest_framework import serializers, exceptions
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
import math
from core.utils import get_age_fun
from crawler.models import CrawlProduct
from mypage.serializers import SimpleSellerInfoSerializer, DeliveryPolicyInfoSerializer
from products.models import Product, ProductImages, ProductLike
from products.supplymentary.models import PurchasedReceipt, PurchasedTime
from products.utils import check_product_url


class ProductFirstSaveSerializer(serializers.ModelSerializer):
    seller = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Product
        fields = ['seller', 'condition', 'shopping_mall', 'product_url']


class CrawlDataSerializer(serializers.ModelSerializer):
    """
    크롤링 데이터를 다루는 serializer 입니다.
    """
    class Meta:
        model = CrawlProduct
        fields = ['thumbnail_image_url',
                  'product_name',
                  'int_price']


class TempCrawlDataSerializer(serializers.ModelSerializer):
    """
    크롤링 실패시 임시 데이터를 다루는 serializer 입니다.
    """
    thumbnail_image_url = serializers.SerializerMethodField(read_only=True)
    product_name = serializers.SerializerMethodField(read_only=True)
    int_price = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = ['thumbnail_image_url',
                  'product_name',
                  'int_price']

    @staticmethod
    def get_thumbnail_image_url(obj):
        return None

    @staticmethod
    def get_product_name(obj):
        return None

    @staticmethod
    def get_int_price(obj):
        return None


class ProductMainSerializer(serializers.ModelSerializer):
    """
    상품 메인페이지 및 찜한 상품 조회에 사용하는 serializer 입니다.
    """
    discount_rate = serializers.SerializerMethodField()
    thumbnail_image_url = serializers.SerializerMethodField(read_only=True)
    int_price = serializers.SerializerMethodField(read_only=True)
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id',
                  'name',
                  'discount_rate',
                  'thumbnail_image_url',
                  'int_price',
                  'price',
                  'is_owner']


    @staticmethod
    def get_discount_rate(obj):
        if not obj.crawl_product_id:
            return None
        crawl_price = CrawlProduct.objects.get(id=obj.crawl_product_id).int_price
        price = obj.price
        rate = round(abs(crawl_price - price) / crawl_price, 2) * 100
        if crawl_price - price > 0:
            return rate
        return None

    @staticmethod
    def get_thumbnail_image_url(obj):
        if not obj.crawl_product_id:
            return obj.images.first().image_url
        return CrawlProduct.objects.get(id=obj.crawl_product_id).thumbnail_image_url

    @staticmethod
    def get_int_price(obj):
        if not obj.crawl_product_id:
            return None
        return CrawlProduct.objects.get(id=obj.crawl_product_id).int_price

    def get_is_owner(self, obj):
        user = self.context['request'].user
        if obj.seller == user:
            return True
        return False


class ProductRetrieveSerializer(serializers.ModelSerializer):
    """
    상품 상세페이지 조회에 사용하는 serializer 입니다.
    """
    crawl_data = serializers.SerializerMethodField()
    receipt_image_url = serializers.SerializerMethodField()
    # name = serializers.SerializerMethodField()
    discount_rate = serializers.SerializerMethodField()
    is_receipt = serializers.SerializerMethodField()
    views = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    images = serializers.SerializerMethodField()

    category = serializers.SerializerMethodField() # category 어떻게 보여줄지?
    size = serializers.SerializerMethodField() # size name!
    size_capture_image = serializers.SerializerMethodField() # 없으면 None
    purchased_year = serializers.SerializerMethodField()
    purchased_month = serializers.SerializerMethodField()

    age = serializers.SerializerMethodField() #ex: 3 days ago

    delivery_policy = serializers.SerializerMethodField()
    seller = SimpleSellerInfoSerializer()

    other_seller_products = serializers.SerializerMethodField()  # def 안에 simple product serializer 활용하여 data return
    related_products = serializers.SerializerMethodField()  # "

    class Meta:
        model = Product
        fields = ['id',
                  'possible_upload', # True 이면 보이고, False 이면 dim 처리
                  'sold',
                  'is_liked',
                  'valid_url', #
                  'age', #
                  'views', #
                  'crawl_data', #
                  'is_receipt', #
                  'shopping_mall',  # 쇼핑몰 로고?
                  'name', 'price', 'discount_rate', #
                  'free_delivery',
                  'content',
                  'images', #
                  'receipt_image_url', #
                  'category', #
                  'size', #
                  'color',
                  'purchased_year', #
                  'purchased_month', #
                  'product_url',
                  'delivery_policy',
                  'seller',
                  'size_capture_image',
                  'other_seller_products',
                  'related_products'
                  ]

    @staticmethod
    def get_valid_url(obj):
        url = obj.product_url
        valid_url = check_product_url(url)
        if valid_url:
            return True
        return False

    @staticmethod
    def get_age(obj):
        return get_age_fun(obj)

    @staticmethod
    def get_views(obj):
        if hasattr(obj, 'views'):
            return obj.views.view_counts
        return 0

    @staticmethod
    def get_crawl_data(obj):
        if obj.crawl_product_id:
            serializer = CrawlDataSerializer(CrawlProduct.objects.get(id=obj.crawl_product_id))
        else:
            serializer = TempCrawlDataSerializer(obj)
        return serializer.data

    def get_is_liked(self, obj):
        user = self.context['request'].user
        liked = ProductLike.objects.filter(product=obj, user=user)
        if liked.exists():
            liked = liked.last()
            return liked.is_liked
        return False

    @staticmethod
    def get_is_receipt(obj):
        if obj.receipt:
            return True
        return False

    @staticmethod
    def get_discount_rate(obj):
        crawl_price = CrawlProduct.objects.get(id=obj.crawl_product_id).int_price
        price = obj.price
        if not price:
            return None
        rate = round(abs(crawl_price - price)/crawl_price, 2) * 100
        if crawl_price - price > 0:
            return rate
        return None

    @staticmethod
    def get_images(obj):
        if not obj.images.exists():
            return []
        images = obj.images.all()
        return ProductImagesRetrieveSerializer(images, many=True).data

    @staticmethod
    def get_receipt_image_url(obj):
        if obj.receipt:
            return obj.receipt.image_url
        else:
            return None

    @staticmethod
    def get_category(obj):
        if obj.category:
            return obj.category.name
        return None

    @staticmethod
    def get_size(obj):
        if obj.size:
            return obj.size.size_name
        return None

    @staticmethod
    def get_purchased_month(obj):
        if obj.purchased_time:
            time = obj.purchased_time
            month = time.month
            return month
        return None

    @staticmethod
    def get_purchased_year(obj):
        if obj.purchased_time:
            time = obj.purchased_time
            year = time.year
            return year
        return None

    @staticmethod
    def get_delivery_policy(obj):
        seller = obj.seller
        if hasattr(seller, 'delivery_policy'):
            return DeliveryPolicyInfoSerializer(seller.delivery_policy).data
        return None

    @staticmethod
    def get_size_capture_image(obj):
        return None

    @staticmethod
    def get_other_seller_products(obj):
        seller = obj.seller
        other_products = Product.objects.filter(is_active=True, possible_upload=True) \
                               .select_related('size', 'size__category', 'seller', 'seller__profile') \
                               .exclude(id=obj.id) \
                               .filter(seller=seller, sold=False) \
                               .distinct().order_by('?')[:5]

        if not other_products:
            return []
        return RelatedProductSerializer(other_products, many=True).data

    @staticmethod
    def get_related_products(obj):
        second_category = obj.category
        related_products = Product.objects.filter(is_active=True, possible_upload=True, temp_save=False) \
                               .select_related('size', 'size__category', 'seller', 'seller__profile') \
                               .exclude(id=obj.id) \
                               .filter(category=second_category, sold=False) \
                               .distinct().order_by('?')[:5]
        if not related_products:
            return []
        return RelatedProductSerializer(related_products, many=True).data


class RelatedProductSerializer(serializers.ModelSerializer):
    thumbnails = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'thumbnails', 'size', 'price', 'name']

    @staticmethod
    def get_thumbnails(obj):
        c_product = CrawlProduct.objects.get(id=obj.crawl_product_id)
        return c_product.thumbnail_image_url

    @staticmethod
    def get_size(obj):
        return obj.size.size_name


class ProductUploadDetailInfoSerializer(serializers.ModelSerializer):
    """
    상품 업로드 과정 중 크롤링된 정보 + (option)구매내역 key를 보여주는 serializer 입니다.
    임시저장 불러올 때는 사용 x
    """
    crawl_data = serializers.SerializerMethodField()
    receipt_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id',
                  'crawl_data',
                  'receipt_image_url',
                  ]

    @staticmethod
    def get_receipt_image_url( obj):
        if obj.receipt:
            return obj.receipt.image_url
        else:
            return None

    @staticmethod
    def get_crawl_data(obj):
        if obj.crawl_product_id:
            serializer = CrawlDataSerializer(CrawlProduct.objects.get(id=obj.crawl_product_id))
        else:
            serializer = TempCrawlDataSerializer(obj)
        return serializer.data


class ProductTempUploadDetailInfoSerializer(serializers.ModelSerializer):
    """
    아마도 임시저장 불러올 때 사용할 것 같음. UploadDetail과 합쳐서 한번에 쓸 수 있었는데 분리한 이유는
    임시저장의 경우 업로드 타입에 따라 아마 client에서 action을 다르게 해야 하기 떄문에 일단 구분함
    * 참고 :name 작성했던게 있으면 name, 없으면 crawl product name (crawl data 안의 product name은 사용 x)
    
    ** category, purchased_time 같이 다른 모델 참고하는 필드는 int(id) 주는데 클라에서 어떻게 할 건지 얘기필요
    """
    receipt_image_url = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    crawl_data = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    purchased_year = serializers.SerializerMethodField()
    purchased_month = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'condition', 'shopping_mall', 'product_url',
                  'crawl_data',
                  'receipt_image_url',
                  'images',
                  'name',
                  'price', 'content', 'free_delivery',
                  'category', 'color', 'size', 'purchased_year', 'purchased_month'
                  ]

    @staticmethod
    def get_crawl_data(obj):
        if obj.crawl_product_id:
            serializer = CrawlDataSerializer(CrawlProduct.objects.get(id=obj.crawl_product_id))
        else:
            serializer = TempCrawlDataSerializer(obj)
        return serializer.data

    @staticmethod
    def get_receipt_image_url(obj):
        if obj.receipt:
            return obj.receipt.image_url
        else:
            return None

    @staticmethod
    def get_images(obj):
        if not obj.images.exists():
            return []
        images = obj.images.all()
        return ProductImagesRetrieveSerializer(images, many=True).data

    @staticmethod
    def get_name(obj):
        if obj.name:
            return obj.name
        if obj.crawl_product_id:
            return CrawlProduct.objects.get(id=obj.crawl_product_id).product_name
        return None

    @staticmethod
    def get_purchased_month(obj):
        if obj.purchased_time:
            time = obj.purchased_time
            month = time.month
            return month
        return None

    @staticmethod
    def get_purchased_year(obj):
        if obj.purchased_time:
            time = obj.purchased_time
            year = time.year
            return year
        return None


class ProductSaveSerializer(serializers.ModelSerializer):
    """
    상품 임시저장 및 최종저장 시 사용하는 serializer 입니다.
    * purchased time의 경우 purchased_year, purchased_month를 입력받아 서버에서 따로 저장합니다.
    * category 의 경우 second_category의 id 를 받습니다.
    """
    class Meta:
        model = Product
        fields = ['name', 'price', 'content', 'free_delivery',
                  'category', 'color', 'size', 'purchased_time', 'possible_upload',
                  'temp_save' # view 에서 넘겨줌
                  ]

    def update(self, obj, validated_data):
        year = validated_data.pop('purchased_year', None)
        month = validated_data.pop('purchased_month', None)
        product = super(ProductSaveSerializer, self).update(obj, validated_data)

        # purchased time save
        if year and month:
            time, _ = PurchasedTime.objects.get_or_create(year=int(year), month=int(month))
            product.purchased_time = time
            product.save()

        return product


class ReceiptSaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchasedReceipt
        fields = ['receipt_image_key']


class ProductImageSaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImages
        fields = '__all__'


class ProductImagesRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImages
        fields = ('image_key', )


# class LikeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ProductLike
#         fields = ['is_liked']