import uuid

from django.db.models import Avg
from rest_framework import serializers, exceptions
from accounts.models import User, Profile
from rest_framework.authtoken.models import Token
from django.utils.translation import ugettext_lazy as _

from accounts.utils import create_token
from push_notifications.models import GCMDevice


class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("phone", "password")

    def validate(self, attrs):
        phone = attrs.get('phone')
        # Did we get back an active user?
        if User.objects.filter(phone=phone, is_banned=True):
            msg = _('User is banned.')
            raise exceptions.ValidationError(msg) # banned user
        elif User.objects.filter(phone=phone, is_active=True):
            msg = _('User is already exists.')
            raise exceptions.ValidationError(msg) # already exists

        return attrs

    def create(self, validated_data):
        uid = uuid.uuid4()
        user = User.objects.create(
            phone=validated_data['phone'],
        )
        user.set_password(validated_data['password'])
        user.uid = uuid.uuid4()
        user.save()
        # 유저 생성될 때 profile instance 생성.
        Profile.objects.get_or_create(user=user)
        # 유저 생성될 떄 GCMDevice instance 생성
        return user

    def update(self, instance, validated_data):
        if validated_data.get('phone'):
            instance.phone = validated_data['phone']
        if validated_data.get('nickname'):
            instance.nickname = validated_data['nickname']
        if validated_data.get('password'):
            instance.set_password(validated_data['password'])
        instance.save()
        return instance


class ResetPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("phone", "password")

    def validate(self, attrs):
        phone = attrs.get('phone')
        # Did we get back an active user?
        if User.objects.filter(phone=phone, is_banned=True):
            msg = _('User is banned.')
            raise exceptions.ValidationError(msg) # banned user
        return attrs

    def update(self, instance, validated_data):
        if validated_data.get('password'):
            instance.set_password(validated_data['password'])
        instance.save()
        return instance


class CredentialException(Exception):
    pass


class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, attrs):
        from django.contrib.auth.hashers import check_password
        super(LoginSerializer, self).validate(attrs)
        phone = attrs.get('phone')
        password = attrs.get('password')

        if phone is None:
            return

        user = User.objects.filter(phone=phone, is_active=True).last()
        attrs['user'] = user

        if user:
            valid_password = check_password(password, user.password)
            if valid_password:
                token, _ = Token.objects.get_or_create(user=user)
                attrs['token'] = token.key
                return attrs
            raise CredentialException("invalid Password")
        raise CredentialException("invalid Email (No User)")


class NicknameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['nickname']


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = ('key',)


class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    review_score = serializers.SerializerMethodField()
    sold = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'nickname', 'profile', 'review_score', 'sold', 'followers']

    def get_sold(self, obj):
        return obj.product_set.filter(sold=True).count()

    def get_review_score(self, obj):
        if obj.received_reviews.first():
            score = obj.received_reviews.all().values('satisfaction'). \
                annotate(score=Avg('satisfaction')).values('score')[0]['score']
            return score
        return 0.0

    def get_followers(self, obj):
        return obj._to.count()

    def get_profile(self, obj):
        return obj.profile.profile_img_url


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Profile
        fields = ['user', 'profile_img']


class ChatUserInfoSerializer(serializers.ModelSerializer):
    profile_img = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'nickname', 'profile_img']

    def get_profile_img(self, obj):
        profile = obj.profile
        return profile.profile_img_url


class UserInfoSerializer(serializers.ModelSerializer):
    seller_registered = serializers.SerializerMethodField()
    token = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'seller_registered', 'token', 'nickname']

    def get_seller_registered(self, user):
        if hasattr(user, 'accounts'):
            return True
        return False

    def get_token(self, user):
        token = create_token(Token, user)
        return token.key


class GCMCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    cloud_message_type = serializers.CharField(default='FCM')

    class Meta:
        model = GCMDevice
        fields = ['user', 'registration_id', 'cloud_message_type']