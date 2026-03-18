from django.db import models

# Create your models here.

class Module(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class CreateBrandsFoundation(models.Model):
    brand_name = models.CharField(max_length=100)
    brand_description = models.TextField()
    image = models.ImageField(upload_to='brand_images/')
    # This can store a list like ["Module1", "Module2"]
    modules = models.ManyToManyField(Module)