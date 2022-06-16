from django.db import models
from datetime import datetime
from django.db.models.fields.related import ForeignKey
from django.utils import timezone


# Create your models here.
class Vip(models.Model):
    name = models.CharField(max_length=32, unique=True)
    mail = models.CharField(max_length=128)
    password = models.CharField(max_length=64)  # SHA256加密后的密码
    avatar = models.CharField(max_length=36, default='default.png')  # MD5摘要算法
    birthday = models.DateField(default=timezone.now)
    level = models.IntegerField(default=0)
    exp = models.IntegerField(default=0)
    money = models.DecimalField(max_digits=65, decimal_places=2, default=0)
    expire_date = models.DateTimeField(default=datetime.fromtimestamp(0, timezone.utc))
    create_date = models.DateTimeField(default=timezone.now)
    is_exist = models.BooleanField(default=True)


class Seat(models.Model):
    condition = models.IntegerField()
    vip_id = models.ForeignKey(Vip, default=None, null=True, on_delete=models.SET_NULL, related_name='seat')
    date = models.DateTimeField()


class Press(models.Model):
    name = models.CharField(max_length=128)
    is_show = models.BooleanField(default=True)


class BookType(models.Model):
    title = models.CharField(max_length=33, unique=True)


class Book(models.Model):
    type = models.ForeignKey(BookType, on_delete=models.RESTRICT, related_name='book')
    name = models.CharField(max_length=128)
    press = models.ForeignKey(Press, on_delete=models.CASCADE, related_name='book')
    pub_data = models.DateField()
    version = models.IntegerField()
    author = models.CharField(max_length=128)
    price = models.DecimalField(max_digits=65, decimal_places=2, default=0)
    page = models.IntegerField()
    desc = models.TextField()
    catalog = models.TextField()
    deal_amount = models.IntegerField(default=0)
    look_amount = models.IntegerField(default=0)
    pic = models.CharField(max_length=36, default='default.png')
    permission = models.IntegerField(default=0)
    is_show = models.BooleanField(default=True)
    is_share = models.BooleanField(default=False)


class ShareBook(models.Model):
    vip_id = models.ForeignKey(Vip, on_delete=models.RESTRICT, related_name='share_book')
    book_id = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='share_date')
    date = models.DateTimeField()


class Post(models.Model):
    title = models.CharField(max_length=128)
    content = models.TextField()
    vip_id = models.ForeignKey(Vip, on_delete=models.CASCADE, related_name='post')
    data = models.DateTimeField()


class PostCommnet(models.Model):
    content = models.TextField()
    vip_id = models.ForeignKey(Vip, on_delete=models.CASCADE, related_name='post_comment')
    data = models.DateTimeField()
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_comment')
    like_amount = models.IntegerField()


class Depart(models.Model):
    name = models.CharField(max_length=32)


class Role(models.Model):
    name = models.CharField(max_length=32)
    parent = models.IntegerField()
    depart = models.ForeignKey(Depart, default=1, on_delete=models.RESTRICT, related_name='role')


class Staff(models.Model):
    name = models.CharField(max_length=32)
    age = models.IntegerField()
    salary = models.DecimalField(max_digits=65, decimal_places=2, default=0)
    card = models.CharField(max_length=32)
    phone = models.CharField(max_length=32)
    role = models.ForeignKey(Role, default=1, on_delete=models.SET_DEFAULT, related_name='staff')
    depart = models.ForeignKey(Depart, on_delete=models.RESTRICT, related_name='staff')
    date = models.DateTimeField(default=timezone.now)


class FoodType(models.Model):
    title = models.CharField(max_length=32, unique=True)


class Food(models.Model):
    type = models.ForeignKey(FoodType, on_delete=models.RESTRICT, related_name='food')
    name = models.CharField(max_length=32)
    price = models.DecimalField(max_digits=65, decimal_places=2, default=0)
    deal_amount = models.IntegerField(default=0)
    avatar = models.CharField(max_length=36, default='default.png')  # use MD5
    memo = models.TextField()


class BookOrder(models.Model):
    vip_id = models.ForeignKey(Vip, null=True, on_delete=models.SET_NULL, related_name='book_order')
    date = models.DateTimeField()
    total_price = models.DecimalField(max_digits=65, decimal_places=2, default=0)
    pay_price = models.DecimalField(max_digits=65, decimal_places=2, default=0)
    status = models.IntegerField()
    cust_name = models.CharField(max_length=32)
    address = models.TextField()
    tel_phone = models.CharField(max_length=32)
    memo = models.TextField()


class BookOrderItem(models.Model):
    order_id = models.ForeignKey(BookOrder, on_delete=models.CASCADE, related_name='order_item')
    book_id = models.ForeignKey(Book, null=True, on_delete=models.SET_NULL, related_name='buy_record')
    amount = models.IntegerField()
    total_price = models.DecimalField(max_digits=65, decimal_places=2, default=0)
    pay_price = models.DecimalField(max_digits=65, decimal_places=2, default=0)


class FoodOrder(models.Model):
    vip_id = models.ForeignKey(Vip, null=True, on_delete=models.SET_NULL, related_name='food_order')
    seat_id = models.ForeignKey(Seat, null=True, on_delete=models.SET_NULL, related_name='food_order')
    date = models.DateTimeField()
    total_price = models.DecimalField(max_digits=65, decimal_places=2, default=0)
    pay_price = models.DecimalField(max_digits=65, decimal_places=2, default=0)
    status = models.IntegerField()
    memo = models.TextField()


class FoodOrderItem(models.Model):
    order_id = models.ForeignKey(FoodOrder, on_delete=models.CASCADE, related_name='order_item')
    food_id = models.ForeignKey(Food, null=True, on_delete=models.SET_NULL, related_name='buy_record')
    amount = models.IntegerField()
    total_price = models.DecimalField(max_digits=65, decimal_places=2, default=0)
    pay_price = models.DecimalField(max_digits=65, decimal_places=2, default=0)


class VipOrder(models.Model):
    vip_id = models.ForeignKey(Vip, null=True, on_delete=models.SET_NULL, related_name='vip_order')
    date = models.DateTimeField()
    total_price = models.DecimalField(max_digits=65, decimal_places=2, default=0)
    pay_price = models.DecimalField(max_digits=65, decimal_places=2, default=0)
    status = models.IntegerField()


class DealType(models.Model):
    title = models.CharField(max_length=32, unique=True)


class Deal(models.Model):
    vip_id = models.ForeignKey(Vip, default=1, on_delete=models.SET_DEFAULT, related_name='deal')
    type = models.ForeignKey(DealType, default=-1, on_delete=models.SET_DEFAULT, related_name='deal_item')
    order_id = models.BigIntegerField()
    amount = models.DecimalField(max_digits=65, decimal_places=2, default=0)
    date = models.DateTimeField()


class BookStore(models.Model):
    book_id = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='book_store')
    amount = models.IntegerField()
    date = models.DateTimeField()


class FoodStore(models.Model):
    food_id = models.ForeignKey(Food, on_delete=models.CASCADE, related_name='food_store')
    amount = models.IntegerField()
    date = models.DateTimeField()
