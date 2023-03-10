from django.db import models
from django.contrib.auth.models import User
import random
from django.utils.text import slugify


severity_level = (
    (1,1),
    (2,2),  
    (3,3),
    (4,4),
    (5,5),
)

ratings_level = (
    (0,0),
    (1,1),
    (1.5,1.5),
    (2,2),
    (2.5,2.5),
    (3,3),
    (3.5,3.5),
    (4,4),
    (4.5,4.5),
    (5,5),
)   


MEMBERSHIP_CHOICES = (
('Premium', 'pre'),
('Free', 'free')
)


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User,blank=False, primary_key=True,on_delete=models.CASCADE)
    auth_token = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class Category(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='images/category')
    def __str__(self):
        return self.name


class Product(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=1000)
    image = models.ImageField(upload_to='images/product')
    prescribed = models.BooleanField(default=False)
    severity = models.IntegerField(choices=severity_level, default=1)
    price = models.IntegerField(default=0)
    margin = models.IntegerField()
    price_before_disc = models.IntegerField(default=0)
    actual_price = models.IntegerField()
    quantity = models.IntegerField()
    in_stock = models.BooleanField(default=False)
    status = models.BooleanField(default=False)
    category = models.ForeignKey(Category,on_delete=models.CASCADE, default=True)
   
    def __str__(self):
        return self.name


    def save(self, *args, **kwargs):
    # """
    # save price as per margin
    # :param args:
    # :param kwargs:
    # :return:
    # """
        self.price = int(self.actual_price) + int((int(self.actual_price) * int(self.margin)) / 100)
        if int(self.price) < 100:
            self.price_before_disc = int(self.price) + random.randint(10, 50)
        elif 100 < int(self.price) < 1000:
            self.price_before_disc = int(self.price) + random.randint(100, 300)
        else:
            self.price_before_disc = int(self.price) + random.randint(300, 800)

        if int(self.quantity) >= 1:
            self.in_stock = True
            self.status = True

        if int(self.quantity) < 1:
            self.in_stock = False
            self.status = False

        super().save(*args, **kwargs)


class Cartitems(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,default=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE,null=True)
    quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return '%s %s'%(self.quantity, self.product.name)


class CheckoutCart(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,default=True)
    cart = models.ForeignKey(Cartitems,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, blank=True, null=True)
    price = models.DecimalField(default=0, max_digits=7, decimal_places=2)
    total = models.DecimalField(max_digits=7, decimal_places=2, default=0) 
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)

 
class Membership(models.Model):
    slug = models.SlugField(null=True, blank=True)
    membership_type = models.CharField(choices=MEMBERSHIP_CHOICES, default='Free',max_length=30)
    price = models.IntegerField(default=0)
    def save(self,*args,**kwargs):
        self.slug =slugify(self.membership_type)
        super(Membership,self).save(*args,**kwargs)


class UserMembership(models.Model):
    user = models.OneToOneField(User,related_name='user_membership', on_delete=models.CASCADE)
    membership = models.ForeignKey(Membership, related_name='user_membership', on_delete=models.SET_NULL, null=True)
    start_date = models.DateTimeField(auto_created=False)
    end_date = models.DateTimeField(auto_created=False)
    active = models.BooleanField(default=False)

    def __str__(self):
       return self.user.username


class ReviewRating(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,default=True)
    products = models.ForeignKey(Product,on_delete=models.CASCADE,default=True) 
    review = models.TextField(max_length=554,null=True)
    ratings = models.IntegerField(choices=ratings_level, default=None)
    created_at = models.DateTimeField(auto_now=True)


class ImportExport(models.Model):
    Medicine = models.CharField(max_length=1000)
    Healthcare= models.CharField(max_length=1000)
    Dosage = models.CharField(max_length=1000)