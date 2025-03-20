from django.db import models
from order.models import Order
from user_manager.models import CustomUser
from inventory.models import Material
from organization.models import Organization

class CarpenterEnquire(models.Model):
    organization_id = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    STATUS_CHOICES = [
        ('requested', 'Requested'),
        ('checking', 'Checking'),
        ('completed', 'Completed)'),
    ]
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='carpenter_enquiries', help_text="Reference to the related order")
    material_id = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='Materials')
    material_length = models.FloatField(help_text="Length in feet", blank=True, null=True)
    material_height = models.FloatField(help_text="Height in feet", blank=True, null=True)
    material_width = models.FloatField(help_text="Width in feet", blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested', help_text="Status of the enquiry")
    carpenter_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='carpenter')
    material_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"Enquiry for Order {self.order_id.id}"

    class Meta:
        verbose_name = "Carpenter Enquiry"
        verbose_name_plural = "Carpenter Enquiries"