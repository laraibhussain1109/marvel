from django.contrib import admin

from .models import InfluencerMetricSnapshot, InfluencerPlatformConnection


@admin.register(InfluencerPlatformConnection)
class InfluencerPlatformConnectionAdmin(admin.ModelAdmin):
    list_display = ("influencer", "platform", "external_account_id", "updated_at")
    list_filter = ("platform",)
    search_fields = ("influencer__username", "external_account_id")


@admin.register(InfluencerMetricSnapshot)
class InfluencerMetricSnapshotAdmin(admin.ModelAdmin):
    list_display = (
        "influencer",
        "source",
        "followers",
        "reach",
        "impressions",
        "engagement_rate",
        "captured_at",
    )
    list_filter = ("source",)
    search_fields = ("influencer__username",)
