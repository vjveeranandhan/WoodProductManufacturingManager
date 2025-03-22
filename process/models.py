from django.db import models
from user_manager.models import CustomUser
from inventory.models import Material
from organization.models import Organization
# Create your models here.
class Process(models.Model):
    name = models.CharField(max_length=100)  # English name, must be unique
    name_mal = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(blank=True, null=True)  # Description in English
    description_mal = models.TextField(blank=True, null=True)
    organization_id = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return self.name

class ProcessDetails(models.Model):
    organization_id = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    PROCESS_STATUS_CHOICES = [
        ('requested', 'Requested'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('verification', 'Verification'),
        ('overdue', 'Overdue'),
    ]
    
    order_id = models.ForeignKey(
        'order.Order',  # String reference
        on_delete=models.CASCADE,
        related_name='process_details',
        help_text="Reference to the related order"
    )
    process_id = models.ForeignKey(
        'process.Process',  # String reference
        on_delete=models.CASCADE,
        related_name='process_details',
        help_text="Reference to the process"
    )
    main_manager_id = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='main_managed_processes',
        help_text="Main manager responsible for this process"
    )
    process_manager_id = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='managed_processes',
        help_text="Manager overseeing this process"
    )
    process_workers_id = models.ManyToManyField(
        CustomUser,
        related_name='worker_processes',
        help_text="Workers involved in the process"
    )
    process_status = models.CharField(
        max_length=20,
        choices=PROCESS_STATUS_CHOICES,
        default='requested',
        help_text="Current status of the process"
    )
    expected_completion_date = models.DateField(
        help_text="Expected date of process completion"
    )
    completion_date = models.DateField(
        help_text="Completion date",
        blank=True,
        null=True,
    )
    workers_salary = models.FloatField(
        help_text="Workers Salary",
        default=0
    )
    material_price = models.FloatField(
        help_text="Material price",
        default=0
    )
    total_price = models.FloatField(
        help_text="Total price for the process",
        default=0
    )
    image = models.ImageField(
        upload_to='process_images/',
        blank=True,
        null=True,
        help_text="Image related to the process"
    )
    over_due = models.BooleanField(default=0)

    request_accepted_date = models.DateField(
        blank=True,
        null=True,
    )

    requested_date = models.DateField(
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"Process Details for Order {self.order_id.id} - Process {self.process_id.id}"
    
class ProcessDetailsImage(models.Model):
    process_details_id = models.ForeignKey(ProcessDetails, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='process_details_images/')

    def __str__(self):
        return f"Image for {self.order.product_name}"
    
class ProcessMaterials(models.Model):
    organization_id = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    process_details_id = models.ForeignKey(
        ProcessDetails,
        on_delete=models.CASCADE,
        related_name='process_materials',
        help_text="Reference to the process details"
    )
    material_id = models.ForeignKey(
        Material,
        on_delete=models.CASCADE,
        related_name='process_materials',
        help_text="Reference to the material"
    )
    quantity = models.IntegerField(default=1,
         help_text="Quantity of the material")
    
    material_price = models.FloatField( 
        help_text="Price of the material"
    )

    total_price = models.FloatField( 
        help_text="Total price"
    )
    def __str__(self):
        return f"Material {self.material_id.id} for Process {self.process_details_id.id}"