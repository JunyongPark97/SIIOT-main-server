from django.conf import settings
from django.db import models

from products.category.models import Bank


class DeliveryPolicy(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='delivery_policy', on_delete=models.CASCADE)
    general = models.IntegerField(verbose_name='일반', default=3000)
    mountain = models.IntegerField(verbose_name='산간지역', default=5000)


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='address', on_delete=models.CASCADE)

    name = models.CharField(max_length=30, verbose_name='이름', default='')
    zipNo = models.CharField(max_length=10, verbose_name='우편번호')
    Addr = models.TextField(verbose_name='주소')
    phone = models.CharField(max_length=19, verbose_name='전화번호')
    detailAddr = models.TextField(verbose_name='상세주소')
    recent = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def address(self):
        """
        주소를 string 형태로 제공하기 위해 사용합니다.
        :return:
        """
        return '({}) {} {}'.format(self.zipNo, self.Addr, self.detailAddr)


class Accounts(models.Model): # todo : 정산계좌, 환불계좌 분리 가능하게
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='accounts', on_delete=models.CASCADE)
    bank = models.ForeignKey(Bank, related_name='accounts', null=True, on_delete=models.SET_NULL)
    bank_accounts = models.TextField()
    accounts_holder = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '계좌'
        verbose_name_plural = '계좌'
