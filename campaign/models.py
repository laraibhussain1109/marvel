from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Campaign(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    total_pay = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    per_deliverable_pay = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    required_deliverables = models.IntegerField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_campaigns")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Deliverable(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="deliverables")
    influencer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="submitted_deliverables")
    deliverable_link = models.URLField(max_length=500, null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.campaign.title} - {self.influencer.username}"

from django.db import models

class CampaignInquiry(models.Model):
    brand_name = models.CharField(max_length=255)
    brand_email = models.EmailField(default=' ')
    brand_contact = models.CharField(max_length=15, default='+91')
    campaign_genre = models.CharField(max_length=255)
    sub_genre = models.CharField(max_length=255)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    target_audience = models.TextField()
    region = models.CharField(max_length=255)
    submitted_at = models.DateTimeField(auto_now_add=True)  # Add this field

    def __str__(self):
        return self.brand_name

