from django.db import models
from django.utils import timezone

# Create your models here.
class User(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(help_text="name", max_length=100)
    department = models.CharField(help_text="department", max_length=100)

class EnterpriseUser(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(help_text="name", max_length=100)
    enterprise = models.CharField(help_text="enterprise", max_length=100)

class Enterprise(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.ForeignKey(User, related_name="enterprise_visible", on_delete=models.CASCADE)
    enterprise = models.CharField(help_text="enterprise", max_length=100)
    deadline = models.DateTimeField()

class Category(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.ForeignKey(User, related_name="category", on_delete=models.CASCADE)
    category = models.CharField(help_text="category", max_length=100) # 얘를 포인트로 탐색

def upload_to_portfolio_thumbnail(instance, filename):
    return f'portfolio_thumbnail/{instance.category_id.user_id.name}/{instance.category_id.category}/{filename}'

class Portfolio(models.Model):
    id = models.BigAutoField(primary_key=True)
    category_id = models.ForeignKey(Category, related_name="portfolio", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    thumbnail_url = models.CharField(max_length=10000, blank=True) # default = ''
    thumbnail_file = models.ImageField(upload_to=upload_to_portfolio_thumbnail, null=True, blank=True) # default null
    title = models.CharField(max_length=100)
    content = models.TextField()
    personal_visible = models.CharField(max_length=10, choices=[('private', "blind"), ('friend', 'friend'), ('public', "open")])
    upload_date = models.DateTimeField(default=timezone.now)