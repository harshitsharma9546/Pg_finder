from django.contrib import admin
from django.utils.html import format_html
from .models import MyUser
# Register your models here.
class MyUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_owner', )
    readonly_fields = ('image_tag',)
    search_fields = ('email', 'username')
    list_filter = ('is_owner', 'is_admin', 'is_staff', 'is_active')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'username', 'first_name', 'last_name', 'date_of_birth', 'phone', 'profile_image','image_tag', 'is_owner', 'aadhar_card', 'address', 'city', 'state', 'pin_code', 'is_admin', 'is_staff', 'is_active', 'is_superadmin')}),
       
    )
    

    def image_tag(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" style="max-height:100px;"/>', obj.profile_image.url)
        return "-"
    image_tag.short_description = 'Profile Image'

admin.site.register(MyUser, MyUserAdmin)

