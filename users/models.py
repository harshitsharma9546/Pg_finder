
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.utils import timezone


class MyUserManager(BaseUserManager):
    def create_user(self, email,username,first_name,last_name, date_of_birth, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError("Users must have an email address")
        

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email,username,first_name,last_name, date_of_birth, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
            date_of_birth=date_of_birth,
        )
        
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using= self._db)
        return user


class MyUser(AbstractBaseUser):
    email = models.EmailField(
        verbose_name="Email Address",
        max_length=255,
        unique=True,
        
    )
    username = models.CharField(max_length=50,unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=30,blank=True,null=True, choices=[
        ('male','Male'),
        ('female','Female'),   
    ])
    date_of_birth = models.DateField(blank=True, null=True)
    phone =  models.CharField(max_length=15,unique=True )
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
  

    is_owner = models.BooleanField(default=False)
    aadhar_card = models.CharField(max_length=20, unique=True, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    pin_code = models.CharField(max_length=10, blank=True, null=True)   

    # required
    date_joined = models.DateTimeField(auto_now_add=True,blank=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)


    objects = MyUserManager()

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = ["username","first_name", "last_name", "date_of_birth"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self,add_label):
        return True
    