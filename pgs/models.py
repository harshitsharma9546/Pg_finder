from django.db import models
from users.models import MyUser as Users

# Create your models here.
class PgListing(models.Model):
    owner = models.ForeignKey(Users, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=200,unique=True)
    description = models.TextField()
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pin_code = models.CharField(max_length=10)
    price_per_month = models.DecimalField(max_digits=10, decimal_places=2)
    available_from = models.DateField(auto_now_add=False)
    is_available = models.BooleanField(default=True)
    type_of_pg = models.CharField(max_length=20,blank=True,null=True, choices=[
        ('boys','Boys'),
        ('girls','Girls'),
        ('coed','Coed'),
        ('family','Family')     
    ])
    amenities = models.TextField(help_text="Comma-separated list of amenities", blank=True, null=True)
    sharing_type = models.CharField(max_length=20, choices=[
        ('single','Single'),
        ('double','Double'),
        ('triple','Triple'),
        ('quad','Quad'),
        
    ])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
class PGImage(models.Model):
    pg = models.ForeignKey(PgListing, on_delete=models.CASCADE, related_name="images")
    pg_image = models.ImageField(upload_to='pg_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.pg.title}"