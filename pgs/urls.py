from django.urls import path
from . import views

urlpatterns = [
    path('', views.pgs, name='pgs'),
    path('about/', views.about, name='about'),     # 👈 yeh upar rakho
    path('search/', views.search, name='search'),
    path('pgregister/', views.pg_register, name='pg_register'),
    path('book/<slug:pg_slug>/', views.book_pg, name='book_pg'),
    path('booking-confirmation/<int:booking_id>/', views.booking_confirmation, name='booking_confirmation'),
    path('confirm-payment/<int:booking_id>/', views.confirm_payment, name='confirm_payment'),
    path('my-bookings/', views.my_bookings_list, name='my_bookings_list'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('<slug:pg_slug>/', views.pg_detail, name='pg_detail'),
]
