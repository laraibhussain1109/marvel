from django.conf import settings
from django.db import models


class InfluencerPlatformConnection(models.Model):
    PLATFORM_FACEBOOK = "facebook"
    PLATFORM_INSTAGRAM = "instagram"
    PLATFORM_YOUTUBE = "youtube"
    PLATFORM_GOOGLE_ANALYTICS = "google_analytics"
    PLATFORM_CHOICES = (
        (PLATFORM_FACEBOOK, "Facebook Page"),
        (PLATFORM_INSTAGRAM, "Instagram Account"),
        (PLATFORM_YOUTUBE, "YouTube Channel"),
        (PLATFORM_GOOGLE_ANALYTICS, "Google Analytics Property"),
    )

    TIER_NANO = "nano"
    TIER_MICRO = "micro"
    TIER_MID = "mid"
    TIER_MACRO = "macro"
    TIER_MEGA = "mega"
    TIER_CHOICES = (
        (TIER_NANO, "Nano Creator (1K-10K)"),
        (TIER_MICRO, "Micro Creator (10K-100K)"),
        (TIER_MID, "Mid-tier Creator (100K-500K)"),
        (TIER_MACRO, "Macro Creator (500K-1M)"),
        (TIER_MEGA, "Mega Creator (1M+)"),
    )

    influencer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="platform_connections",
    )
    platform = models.CharField(max_length=30, choices=PLATFORM_CHOICES)
    external_account_id = models.CharField(max_length=255)
    profile_handle = models.CharField(max_length=255, blank=True)
    access_token = models.TextField(help_text="OAuth access token for this account")
    refresh_token = models.TextField(blank=True, null=True)
    latest_followers = models.PositiveIntegerField(default=0)
    creator_tier = models.CharField(max_length=20, choices=TIER_CHOICES, blank=True)
    connected_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("influencer", "platform", "external_account_id")

    def __str__(self):
        return f"{self.influencer.username} - {self.platform}"

    @staticmethod
    def resolve_creator_tier(audience_size):
        if audience_size >= 1_000_000:
            return InfluencerPlatformConnection.TIER_MEGA
        if audience_size >= 500_000:
            return InfluencerPlatformConnection.TIER_MACRO
        if audience_size >= 100_000:
            return InfluencerPlatformConnection.TIER_MID
        if audience_size >= 10_000:
            return InfluencerPlatformConnection.TIER_MICRO
        return InfluencerPlatformConnection.TIER_NANO


class InfluencerMetricSnapshot(models.Model):
    influencer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="metric_snapshots",
    )
    connection = models.ForeignKey(
        InfluencerPlatformConnection,
        on_delete=models.CASCADE,
        related_name="snapshots",
        null=True,
        blank=True,
    )
    source = models.CharField(max_length=30, choices=InfluencerPlatformConnection.PLATFORM_CHOICES)
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
    raw_payload = models.JSONField(default=dict, blank=True)
    captured_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-captured_at",)

    def __str__(self):
        return f"{self.influencer.username} - {self.source} - {self.captured_at:%Y-%m-%d}"
