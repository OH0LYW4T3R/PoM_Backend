from django.db import models

# Create your models here.
class User(models.Model):
    id = models.BigAutoField(primary_key=True)
    department = models.CharField(help_text="department", max_length=100)