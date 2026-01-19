from django.db import models
from djnago.contrib.auth.model import User
from products.models import Product
# Create your models here.
class Cart(model.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Cart"