from django.urls import path
from .views import (UserCreate, UnitCreate, UnitListView, EquipmentSummaryView, EquipmentDetailView, LoginView, 
AddToCartView, CartView, CheckoutView, ReturnEquipmentView, UserProfileView, UserCheckedOutEquipmentView, TransactionCalendarView)

urlpatterns = [
    path('register/', UserCreate.as_view(), name='user-create'),
    path('unit/', UnitCreate.as_view(), name='unit-create'),
    path('unit/all/', UnitListView.as_view(), name='unit-list'),
    path('equipment-summary/', EquipmentSummaryView.as_view(), name='equipment-summary'), 
    path('equipment/<int:equipment_id>/', EquipmentDetailView.as_view(), name='equipment-detail'),
    path('login/', LoginView.as_view(), name='user-login'),
    path('add-to-cart/', AddToCartView.as_view(), name='add-to-cart'),
    path('cart/', CartView.as_view(), name='cart-view'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('cart/return/', ReturnEquipmentView.as_view(), name='return-equipment'),
    path('profile/', UserProfileView.as_view(), name='profile-view'),
    path('user/equipment-checked-out/', UserCheckedOutEquipmentView.as_view(), name='equipment-checked-out'),
    path("transactions/", TransactionCalendarView.as_view(), name="transaction-cart"),
]