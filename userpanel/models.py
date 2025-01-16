from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin



class Subscription(models.Model):
    Id = models.AutoField(primary_key=True)
    month = models.IntegerField()
    price_sub = models.IntegerField()



class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)  # تنظیم رمز عبور
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=32)
    email = models.EmailField(max_length=32, unique=True)
    phone_number = models.CharField(max_length=11)
    is_active = models.BooleanField(default=True)
    is_check_phone = models.BooleanField(default=False)
    is_block = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    end_date_sub = models.DateTimeField(default=None, null=True, blank=True)
    subscription = models.ForeignKey('Subscription', on_delete=models.CASCADE, null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['name', 'email']

    def __str__(self):
        return self.username

    async def asave(self, *args, **kwargs):
        """Custom save method that supports async."""
        await super().save(*args, **kwargs)



class Order(models.Model):
    Id = models.AutoField(primary_key=True)    
    is_pay = models.BooleanField(default=False)
    create_date = models.DateTimeField()
    subscription = models.ForeignKey(Subscription,on_delete=models.CASCADE,default=None)
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)


class Signal(models.Model):
    Id =models.AutoField(primary_key=True)
    currency = models.CharField(max_length=10)
    stop_loss = models.CharField(max_length=50)
    leverage = models.CharField(max_length=10)
    entry_price = models.CharField(max_length=50)
    margin = models.CharField(max_length=10)
    status = models.CharField(max_length=10,default="")

    signal_type = models.CharField(default='')
    is_free = models.BooleanField(default=False)
    date_added = models.DateTimeField(default=None)
    signal_code = models.IntegerField(default=0)
    signal_text = models.CharField(max_length=500,default="")
class SignalProfit(models.Model):
    Id = models.AutoField(primary_key=True)
    signal_profit = models.TextField(max_length=50)
    signal = models.ForeignKey(Signal,on_delete=models.CASCADE)
    is_outed = models.BooleanField(default=False)   
    is_lossed = models.BooleanField(default=False)


class SignalGain(models.Model):
    Id = models.AutoField(primary_key=True)
    pictureName = models.CharField(max_length=50)
    description = models.CharField(max_length=800,default="")
    signal = models.ForeignKey(Signal,on_delete=models.CASCADE)



    