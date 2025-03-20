from django.db import models
from organization.models import Organization
# Create your models here.

class InventoryCategory(models.Model):
    organization_id = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Material(models.Model):
    organization_id = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    STOCK_AVAILABILITY_CHOICES = [
        ('in_stock', 'In Stock'),
        ('low_stock', 'Low Stock'),
        ('out_of_stock', 'Out of Stock'),
    ]
    code = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=100)
    name_mal = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    description_mal = models.TextField(blank=True, null=True)
    colour = models.TextField(blank=True, null=True)
    quality = models.TextField(blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    durability = models.TextField(blank=True, null=True)
    stock_availability = models.CharField(
        max_length=20,
        choices=STOCK_AVAILABILITY_CHOICES,
        default='in_stock'
    )
    price = models.FloatField(default=0.0)
    category_id = models.ForeignKey('InventoryCategory', on_delete=models.PROTECT, related_name='materials')
    reference_image = models.ImageField(upload_to='material_images/', blank=True, null=True)
    mrp_in_gst = models.FloatField(default=0.0)

    def __str__(self):
        return self.name

class MaterialImages(models.Model):
    material_id = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='material_images')
    image = models.ImageField(upload_to='material_images/')