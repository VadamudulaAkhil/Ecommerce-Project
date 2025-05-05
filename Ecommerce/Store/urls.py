from django.urls import path
from Store import views

urlpatterns = [
    path('Cart/', views.Cart, name='Cart'),
    path('Checkout/', views.Checkout, name='Checkout'),
    path('update_item/', views.UpdateItem, name='update_item'),
    path('process_order/', views.ProcessOrder, name='process_order'),
    path('', views.Items, name='store'),
] 

