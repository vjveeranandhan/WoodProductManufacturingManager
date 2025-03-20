from django.db import models

class Organization(models.Model):
    name = models.CharField(max_length=255, unique=True)
    registration_number = models.CharField(max_length=100, unique=True, help_text="Govt registration number")
    established_date = models.DateField(null=True, blank=True)
    industry_type = models.CharField(
        max_length=255,
        choices=[
            ('TEXTILE', 'Textile'),
            ('WOOD', 'Wood'),
            ('PLASTIC', 'Plastic'),
            ('METAL', 'Metal'),
            ('FOOD', 'Food Processing'),
            ('OTHER', 'Other')
        ]
    )
    
    # Contact Details
    email = models.EmailField(unique=True)
    phone_number1 = models.CharField(max_length=15, unique=True)
    phone_number2 = models.CharField(max_length=15, unique=True)
    website = models.URLField(null=True, blank=True)

    # Address Details
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='India')
    postal_code = models.CharField(max_length=10)

    # Legal & License Details
    gst_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    pan_number = models.CharField(max_length=10, unique=True, blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name
