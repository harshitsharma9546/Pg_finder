from django.contrib import admin
from .models import PgListing, PGImage, Booking
# Register your models here.

class PgListingAdmin(admin.ModelAdmin):
    list_display = ('title','owner', 'city', 'state', 'price_per_month',)
    prepopulated_fields = {'slug' : ('title',)}
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "owner":
            kwargs["queryset"] = db_field.related_model.objects.filter(is_owner=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class PGImageAdmin(admin.ModelAdmin):
    list_display = ('pg', 'uploaded_at',)

class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'tenant', 'pg', 'amount', 'status', 'booking_date', 'visit_later')
    list_filter = ('status', 'booking_date', 'visit_later')
    search_fields = ('tenant__username', 'pg__title', 'id')
    readonly_fields = ('booking_date', 'qr_code')
    
admin.site.register(PgListing,PgListingAdmin)
admin.site.register(PGImage, PGImageAdmin)
admin.site.register(Booking, BookingAdmin)

