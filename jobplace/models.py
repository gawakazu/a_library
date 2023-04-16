from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class PublisherModel(models.Model):
    publisher = models.CharField(max_length=50)
    publisher2 = models.CharField(max_length=50)
    def __str__(self):
        return self.publisher

class AuthorModel(models.Model):
    author = models.CharField(max_length=50)
    author2 = models.CharField(max_length=50)
    def __str__(self): 
        return self.author

class LibraryModel(models.Model):
    library = models.CharField(max_length=50)
    location = models.CharField(max_length=50)
    location_map = models.ImageField(upload_to='')
    def __str__(self):
        return self.library

class BookModel(models.Model):
    book = models.CharField(max_length=100)
    book2 = models.CharField(max_length=100)
    book3 = models.CharField(max_length=100)
    number = models.CharField(max_length=100)
    images = models.CharField(max_length=100,blank=True,null=True)
    #images = models.ImageField(upload_to='images/')    
    year = models.CharField(max_length=100)
    author = models.ForeignKey(AuthorModel,on_delete=models.CASCADE)
    library = models.ForeignKey(LibraryModel,on_delete=models.CASCADE)
    publisher = models.ForeignKey(PublisherModel,on_delete=models.CASCADE)
    def __str__(self):
        return self.book

class CustomUser(AbstractUser):
    class Meta(AbstractUser.Meta):
        pass
    address = models.CharField(max_length=50)
    age = models.IntegerField('年齢',blank=True,null=True)
    zip_code = models.CharField(max_length=50)

class ReservationModel(models.Model):
    book = models.ForeignKey(BookModel,on_delete=models.CASCADE)
    #library = models.ForeignKey(LibraryModel,on_delete=models.CASCADE)
    reservation_date = models.DateTimeField(verbose_name='予約日',auto_now=True)
    start_date = models.DateField(verbose_name='貸出日',blank=True,null=True)
    end_date = models.DateField(verbose_name='返却日',blank=True,null=True)
    limited_date = models.DateField(verbose_name='取置期限',blank=True,null=True)
    status = models.CharField(max_length=50,blank=True,null=True)
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)


class HistoryModel(models.Model):
    book = models.ForeignKey(BookModel,on_delete=models.CASCADE)
    #library = models.ForeignKey(LibraryModel,on_delete=models.CASCADE)
    #reservation_day = models.DateTimeField(verbose_name='予約日')
    start_day = models.DateField(verbose_name='貸出日')
    end_day = models.DateField(verbose_name='返却日')
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)

class CommentModel(models.Model):
    comment  = models.TextField()
    status = models.CharField(max_length=50,blank=True,null=True)

