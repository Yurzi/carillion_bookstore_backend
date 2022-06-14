from django.db import models
from django.db.models.fields import DecimalField

# Create your models here.
class Vip(models.Model):
    name = models.CharField(max_length= 32)
    mail = models.CharField(max_length= 128)
    password = models.CharField(max_length= 64)    # SHA256加密后的密码
    avatar = models.CharField(max_length= 32)       # MD5摘要算法
    birthday = models.DateField()
    level = models.IntegerField()
    expire_data = models.DateTimeField()
    create_data = models.DateTimeField()

class Seat(models.Model):
    condition = models.IntegerField()
    vip_id = models.ForeignKey(Vip, on_delete= models.RESTRICT)
    data = models.DateTimeField()

class Press(models.Model):
    name = models.CharField(max_length= 128)
    is_show = models.BooleanField()

class BookType(models.Model):
    title = models.CharField(max_length= 32)

class Book(models.Model):
    type = models.ForeignKey(BookType, on_delete=models.RESTRICT)
    name = models.CharField(max_length= 128)
    press = models.ForeignKey(Press, on_delete=models.RESTRICT)
    pub_data = models.DateField()
    version = models.IntegerField()
    author = models.CharField(max_length= 128)
    price = models.DecimalField(max_digits= 65, decimal_places= 2)
    page = models.IntegerField()
    desc = models.TextField()
    catalog = models.TextField()
    deal_amount = models.IntegerField()
    look_amount = models.IntegerField()
    pic = models.CharField(max_length= 32)
    permission = models.IntegerField()
    is_show = models.BooleanField()

class ShareBook(models.Model):
    vip_id = models.ForeignKey(Vip, on_delete= models.RESTRICT)
    book_id = models.ForeignKey(Book, on_delete= models.RESTRICT)
    data = models.DateTimeField()

class Post(models.Model):
    title = models.CharField(max_length= 128)
    content = models.TextField()
    vip_id = models.ForeignKey(Vip, on_delete=models.CASCADE)
    data = models.DateTimeField()

class PostCommnet(models.Model):
    content = models.TextField()
    vip_id = models.ForeignKey(Vip, on_delete= models.CASCADE)
    data = models.DateTimeField()
    post_id = models.ForeignKey(Post, on_delete= models.CASCADE)
    like_amount = models.IntegerField()

class Depart(models.Model):
    name = models.CharField(max_length= 32)

class Role(models.Model):
    name = models.CharField(max_length= 32)

class Staff(models.Model):
    name = models.CharField(max_length= 32)
    age = models.IntegerField()
    salary = models.DecimalField(max_digits= 65, decimal_places= 2)
    card = models.CharField(max_length= 32)
    phone = models.CharField(max_length= 32)
    role = models.ForeignKey(Role, default= 0, on_delete= models.SET_DEFAULT)
    depart = models.ForeignKey(Depart, on_delete= models.RESTRICT)

class FoodType(models.Model):
    title = models.CharField(max_length= 32)

class Food(models.Model):
    type = models.ForeignKey(FoodType, on_delete=models.RESTRICT)
    name = models.CharField(max_length= 32)
    price = models.DecimalField(max_digits=65, decimal_places=2)
    deal_amount = models.IntegerField()
    avatar = models.CharField(max_length= 32)   # use MD5
    memo = models.TextField()

class BookOrder(models.Model):
    vip_id = models.ForeignKey(Vip, null= True, on_delete= models.SET_NULL)
    data = models.DateTimeField()
    total_price = models.DecimalField(max_digits= 65, decimal_places= 2)
    pay_price = models.DecimalField(max_digits= 65, decimal_places= 2)
    status = models.IntegerField()
    cust_name = models.CharField(max_length= 32)
    address = models.TextField()
    tel_phone = models.CharField(max_length= 32)
    memo = models.TextField()

class BookOrderItem(models.Model):
    order_id = models.ForeignKey(BookOrder, on_delete= models.CASCADE)
    book_id = models.ForeignKey(Book, null= True, on_delete= models.SET_NULL)
    amount = models.IntegerField()
    total_price = models.DecimalField(max_digits= 65, decimal_places= 2)
    pay_price = models.DecimalField(max_digits= 65, decimal_places= 2)

class FoodOrder(models.Model):
    vip_id = models.ForeignKey(Vip, null= True, on_delete= models.SET_NULL)
    seat_id = models.ForeignKey(Seat, null= True, on_delete= models.SET_NULL)
    data = models.DateTimeField()
    total_price = models.DecimalField(max_digits= 65, decimal_places= 2)
    pay_price = models.DecimalField(max_digits= 65, decimal_places= 2)
    status = models.IntegerField()
    memo = models.TextField()

class FoodOrderItem(models.Model):
    order_id = models.ForeignKey(FoodOrder, on_delete= models.CASCADE)
    food_id = models.ForeignKey(Food, null= True, on_delete= models.SET_NULL)
    amount = models.IntegerField()
    total_price = models.DecimalField(max_digits= 65, decimal_places= 2)
    pay_price = models.DecimalField(max_digits= 65, decimal_places= 2)

class Deal(models.Model):
    type = models.IntegerField()
    order_id = models.BigIntegerField()
    amount = models.DecimalField(max_digits= 65, decimal_places= 2)
    data = models.DateTimeField()

class BookStore(models.Model):
    book_id = models.ForeignKey(Book, on_delete=models.CASCADE)
    amount = models.IntegerField()
    data = models.DateTimeField()

class FoodStore(models.Model):
    food_id = models.ForeignKey(Food, on_delete=models.CASCADE)
    amount = models.IntegerField()
    data = models.DateTimeField()
