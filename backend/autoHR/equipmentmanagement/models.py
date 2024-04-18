from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist


class Unit(models.Model):
    name = models.CharField(max_length=100)
    uic = models.CharField(max_length=10)

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    rank = models.CharField(max_length=255)
    unit = models.ForeignKey('Unit', on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        # Check whether this is a new record or an existing one
        creating = self._state.adding
        super(UserProfile, self).save(*args, **kwargs)

        if creating:
            try:
                cart = self.cart
            except ObjectDoesNotExist:
                Cart.objects.create(user_profile=self)
class Equipment(models.Model):
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('borrowed', 'Borrowed'),
        ('maintenance', 'Maintenance'),
        ('turn-in', 'Turn-in')
    )
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='equipments')
    name = models.CharField(max_length=100)
    nsn = models.CharField(max_length = 20, blank = True, null = True)
    lin = models.CharField(max_length=50, blank = True, null = True)
    serial_number = models.CharField(max_length=100)
    location = models.CharField(max_length = 25)
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices = STATUS_CHOICES, default='Available')  

    def __str__(self):
        return self.name
    
class Cart(models.Model):
    user_profile = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='cart', 
        null=True,
        blank=True
    )
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='cart_items', null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    transaction = models.ForeignKey('Transaction', on_delete=models.SET_NULL, null=True, blank=True, related_name='cart_items')

    def __str__(self):
        return f"{self.equipment.name} - {self.quantity}"

class Transaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    checkout_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField(null=True, blank=True)
    expected_return_date = models.DateTimeField(null =True, blank = True)

    status = models.CharField(max_length=20, choices = [('available', 'Available'),
        ('borrowed', 'Borrowed'),
        ('maintenance', 'Maintenance'),
        ('turn-in', 'Turn-in'), 
        ('returned', 'Returned')])
    

    def __str__(self):
        return f"{self.equipment.name} - {self.user.username}"

    def save(self, *args, **kwargs):
        if self.status == 'returned' and not self.actual_return_date:
            self.actual_return_date  = timezone.now()
        super().save(*args, **kwargs)