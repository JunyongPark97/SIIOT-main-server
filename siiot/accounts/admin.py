from django.contrib import admin
from django.contrib.auth.models import Permission
from django import forms
from rest_framework.authtoken.models import Token
from accounts.nickname.models import FirstNickName, LastNickName
from custom_manage.sites import superadmin_panel, staff_panel
from custom_manage.tools import superadmin_register
from .models import User, PhoneConfirm, Profile

from push_notifications.models import GCMDevice

class UserSuperadminForm(forms.ModelForm):
    user_permissions = forms.ModelMultipleChoiceField(
        Permission.objects.all(),
        widget=admin.widgets.FilteredSelectMultiple('user_permissions', False),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super(UserSuperadminForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.initial['user_permissions'] = self.instance.user_permissions.values_list('pk', flat=True)


class UserSuperadmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'nickname', 'is_active']
    search_fields = ['email', 'phone']
    form = UserSuperadminForm
    actions = ['apply_staff_permission']

    def apply_staff_permission(self, request, queryset):
        park = User.objects.get(pk=2)
        permission_object_ids = park.user_permissions.all().values_list('id', flat=True)
        rows_updated = 0
        for user in queryset.exclude(id=park.id):
            user.user_permissions.clear()
            user.user_permissions.add(*permission_object_ids)
            rows_updated += 1
        self.message_user(request, '%d개의 아이디에 staff 권한을 적용했습니다.' % rows_updated)


class TokenStaffAdmin(admin.ModelAdmin):
    list_display = ['key', 'user', 'created']


superadmin_panel.register(User, UserSuperadmin)
superadmin_panel.register(Token, TokenStaffAdmin)

superadmin_register(Profile, list_display=['id', 'user'], user_fields=['user', ])
superadmin_register(PhoneConfirm, list_display=['phone', 'certification_number', 'is_confirmed', 'temp_key', 'created_at'])


# staff

class UserStaffadmin(admin.ModelAdmin):
    list_display = ['id', 'phone', 'email', 'nickname', 'is_active', 'created_at']
    search_fields = ['email', 'phone']


class PhoneConfirmAdmin(admin.ModelAdmin):
    list_display = ['phone', 'certification_number', 'is_confirmed', 'temp_key', 'created_at']


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'profile_img']


class FirstNicknameAdmin(admin.ModelAdmin):
    list_display = ['first_nickname', 'is_active', 'created_at']


class LastNicknameAdmin(admin.ModelAdmin):
    list_display = ['last_nickname', 'is_active', 'created_at']


class GCMDeviceAdmin(admin.ModelAdmin):
    list_display = ['registration_id', 'user']


staff_panel.register(User, UserStaffadmin)
staff_panel.register(PhoneConfirm, PhoneConfirmAdmin)
staff_panel.register(Profile, ProfileAdmin)
staff_panel.register(FirstNickName, FirstNicknameAdmin)
staff_panel.register(LastNickName, LastNicknameAdmin)
staff_panel.register(GCMDevice, GCMDeviceAdmin)
