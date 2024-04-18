from django.contrib import admin

# Register your models here.
from .models import UserProfile, Unit, Equipment, Transaction, CartItem, Cart   

admin.site.register(Unit)
admin.site.register(Equipment)
admin.site.register(Transaction)
admin.site.register(CartItem)
admin.site.register(Cart)

class UserProfileAdmin(admin.ModelAdmin):
    exclude = ('cart',)
admin.site.register(UserProfile, UserProfileAdmin)