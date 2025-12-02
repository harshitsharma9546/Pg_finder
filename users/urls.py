from django.urls import path
from . import views

urlpatterns = [
  path('login/', views.user_login, name='user_login'),
  path('signup/', views.signup, name='signup'),
  path('client/register/', views.client_register, name='client_register'),
  path('owner/register/', views.owner_register, name='owner_register'),
  path('activate/<uidb64>/<token>/',views.activate,name='activate'),
  path('logout/', views.user_logout, name='user_logout'),
  path('forgot-password/', views.forgotPassword, name='forgotPassword'),
  path('resetpassword_validate/<uidb64>/<token>/',views.resetpassword_validate,     name='resetpassword_validate'),
  path('resetPassword/',views.resetPassword,name='resetPassword'),


  path('terms-and-conditions/', views.terms_conditions, name='terms_conditions'),
]