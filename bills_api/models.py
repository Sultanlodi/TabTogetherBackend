# TapTogetherBackend/bills_api/models.py

from django.db import models
from django.contrib.auth.models import User # If you plan to have users

class Bill(models.Model):
    # If you have users, link the bill to a user (uncomment and adjust if you implement user authentication)
    # user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bills')
    uploaded_image = models.ImageField(upload_to='bills/%Y/%m/%d/') # Images will be saved in media/bills/year/month/day
    upload_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    # This field could store the raw JSON response from Gemini, or a parsed version
    gemini_raw_response = models.JSONField(null=True, blank=True)
    is_processed = models.BooleanField(default=False) # To track if Gemini processing was successful

    def __str__(self):
        return f"Bill {self.id} on {self.upload_date.strftime('%Y-%m-%d')}"

class BillItem(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='items') # Links items to a specific bill
    description = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # Add fields to track who paid for what, e.g.:
    # assigned_to = models.ManyToManyField(User, related_name='paid_items', blank=True)

    def __str__(self):
        return f"{self.description} - ${self.price} (Bill {self.bill.id})"