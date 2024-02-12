from django.urls import path, re_path
from . import views
urlpatterns = [
    path('item-list/',views.getAllItems),
    path('item-detail/',views.getItem),
    path('item-update/',views.updateItem),
    path('item-create/',views.createItem),
    path('item-delete/',views.deleteItem),
    path('category-list/',views.getAllCategories),
    path('category-create/',views.createCategory),
    path('category-delete/',views.delete_category),
    re_path('authentication/login', views.login),
    re_path('authentication/signup', views.signup),
    re_path('authentication/testtoken', views.testToken),
    re_path('authentication/forgot-password', views.forgot_password),
    re_path('authentication/reset-password/<str:uidb64>/<str:token>', views.reset_password),
]
 
