from django.conf import settings
from django.db import models


class InfluencerPlatformConnection(models.Model):
    PLATFORM_META = "meta"
    PLATFORM_INSTAGRAM = "instagram"
    PLATFORM_GOOGLE = "google"
    PLATFORM_CHOICES = (
        (PLATFORM_META, "Meta Graph API"),
        (PLATFORM_INSTAGRAM, "Instagram Graph API"),
        (PLATFORM_GOOGLE, "Google API"),
    )

    influencer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="platform_connections",
    )
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    external_account_id = models.CharField(max_length=255)
    access_token = models.TextField(
        help_text="OAuth access token issued by the selected platform."
    )
    refresh_token = models.TextField(blank=True, null=True)
    connected_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("influencer", "platform", "external_account_id")

    def __str__(self):
        return f"{self.influencer.username} - {self.platform}"


class InfluencerMetricSnapshot(models.Model):
    influencer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="metric_snapshots",
    )
    source = models.CharField(max_length=20, choices=InfluencerPlatformConnection.PLATFORM_CHOICES)
    followers = models.PositiveIntegerField(default=0)
    profile_views = models.PositiveIntegerField(default=0)
    reach = models.PositiveIntegerField(default=0)
    impressions = models.PositiveIntegerField(default=0)
    page_views = models.PositiveIntegerField(default=0)
    engagement = models.PositiveIntegerField(default=0)
    engagement_rate = models.FloatField(default=0)
    location = models.CharField(max_length=255, blank=True)
    gender_split = models.JSONField(default=dict, blank=True)
    city_split = models.JSONField(default=dict, blank=True)
    captured_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-captured_at",)

    def __str__(self):
        return f"{self.influencer.username} - {self.source} - {self.captured_at:%Y-%m-%d}"
