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

from django.db import models
import copy  # Needed for default

class CampaignInquiry(models.Model):
    CREATOR_TYPE_CHOICES = [
    ('Nano', 'Nano'),
    ('Micro', 'Micro'),
    ('Macro', 'Macro'),
    ('Mega', 'Mega'),
    ('Mega A+', 'Mega A+'),
    ('Celebrities', 'Celebrities'),
    ('Premium Celebrities', 'Premium Celebrities'),
    ]

    BUDGET_CHOICES = [
        ('Can’t disclose', 'Can’t disclose'),
        ('0-3 Lakhs', '0-3 Lakhs'),
        ('3-5 Lakhs', '3-5 Lakhs'),
        ('5-10 Lakhs', '5-10 Lakhs'),
        ('10-20 Lakhs', '10-20 Lakhs'),
        ('20-50 Lakhs', '20-50 Lakhs'),
        ('50 Lakhs+', '50 Lakhs+'),
    ]
    PLATFORM_CHOICES = [
        ('Instagram', 'Instagram'),
        ('YouTube', 'YouTube'),
        ('Facebook', 'Facebook'),
        ('Twitter', 'Twitter'),
        ('Snapchat', 'Snapchat'),
        ('LinkedIn', 'LinkedIn'),
        ('Moj', 'Moj'),
        ('Josh', 'Josh'),
        ('Koo', 'Koo'),
        ('ShareChat', 'ShareChat'),
        ('TikTok', 'TikTok'),
    ]
    SERVICE_CHOICES = [
        ('Influencer Marketing', 'Influencer Marketing'),
        ('Celebrity Marketing', 'Celebrity Marketing'),
        ('Visit Store/Place', 'Visit Store/Place'),
        ('Barter Campaign', 'Brarter Campaign'),
        ('UGC', 'UGC'),
        ('Celebrity Endorsement', 'Celebrity Endorsement'),   
        ('Digital Marketing', 'Digital Marketing'),
        ('Other', 'Other'),
    ]

    CREATOR_GENRE_CHOICES = [
        ('Fashion', 'Fashion'),
        ('Beauty', 'Beauty'),
        ('Lifestyle', 'Lifestyle'),
        ('Food', 'Food'),
        ('Travel', 'Travel'),
        ('Fitness', 'Fitness'),
        ('Gaming', 'Gaming'),
        ('Technology', 'Technology'),
        ('Entertainment', 'Entertainment'),
        ('Education', 'Education'),
        ('Finance', 'Finance'),
        ('Health', 'Health'),
        ('Real Estate', 'Real Estate'),
    ]
       

    brand_name = models.CharField(max_length=255)
    brand_email = models.EmailField(default=' ')
    brand_contact = models.CharField(max_length=15, default='+91')
    # campaign_genre = models.CharField(max_length=255)
    # sub_genre = models.CharField(max_length=255)
    service = models.CharField(
        max_length=50,
        choices=SERVICE_CHOICES,
        default='Influencer Marketing'
    )
    creator_genre = models.JSONField(
        default=list,
        blank=True,
        help_text="Select any three or more creator genres"
    )
    describe_your_campaign = models.TextField()
    Timeline = models.CharField(
        max_length=20,
        choices=[('1 time', '1 time')] + [(f'{i} month{"s" if i > 1 else ""}', f'{i} month{"s" if i > 1 else ""}') for i in range(1, 49)],
        default='1 time'
    )
    region = models.CharField(max_length=255)


    select_influencer_platform = models.JSONField(
        default=list,
        blank=True,
        help_text="Select one or more platforms"
    )
    creator_type = models.CharField(
        max_length=50,
        choices=CREATOR_TYPE_CHOICES,
        default='Nano'
    )
    budget_range = models.CharField(
        max_length=50,
        choices=BUDGET_CHOICES,
        default='Can’t disclose'
    )

    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.brand_name


