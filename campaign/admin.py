import csv

from django.contrib import admin
from django.http import HttpResponse

from .models import Campaign, CampaignInquiry, Deliverable


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ("title", "created_by", "created_at", "total_pay")
    list_filter = ("created_by", "created_at")
    search_fields = ("title", "created_by__username")

    actions = ["generate_campaign_report"]

    def generate_campaign_report(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="campaign_report.csv"'
        writer = csv.writer(response)
        writer.writerow(
            [
                "Brand Name",
                "Campaign Title",
                "Influencer",
                "Deliverable Link",
                "Is Approved",
                "Submitted At",
                "Total Deliverables",
                "Approved Deliverables",
            ]
        )

        for campaign in queryset:
            deliverables = Deliverable.objects.filter(campaign=campaign)
            approved_count = deliverables.filter(is_approved=True).count()
            for deliverable in deliverables:
                writer.writerow(
                    [
                        campaign.created_by.username,
                        campaign.title,
                        deliverable.influencer.username,
                        deliverable.deliverable_link or "N/A",
                        "Yes" if deliverable.is_approved else "No",
                        deliverable.submitted_at.strftime("%Y-%m-%d %H:%M:%S"),
                        campaign.required_deliverables,
                        approved_count,
                    ]
                )
        return response

    generate_campaign_report.short_description = "Generate Campaign Report"


@admin.register(Deliverable)
class DeliverableAdmin(admin.ModelAdmin):
    list_display = ("campaign", "influencer", "is_approved", "submitted_at")
    list_filter = ("campaign", "influencer", "is_approved")
    search_fields = ("campaign__title", "influencer__username")

    actions = ["generate_deliverable_report"]

    def generate_deliverable_report(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="deliverable_report.csv"'
        writer = csv.writer(response)
        writer.writerow(
            [
                "Campaign Title",
                "Influencer",
                "Deliverable Link",
                "Is Approved",
                "Submitted At",
            ]
        )

        for deliverable in queryset:
            writer.writerow(
                [
                    deliverable.campaign.title,
                    deliverable.influencer.username,
                    deliverable.deliverable_link or "N/A",
                    "Yes" if deliverable.is_approved else "No",
                    deliverable.submitted_at.strftime("%Y-%m-%d %H:%M:%S"),
                ]
            )
        return response

    generate_deliverable_report.short_description = "Generate Deliverable Report"


@admin.register(CampaignInquiry)
class CampaignInquiryAdmin(admin.ModelAdmin):
    list_display = ("brand_name", "brand_email", "campaign_genre", "budget", "submitted_at")
    list_filter = ("campaign_genre", "region", "submitted_at")
    search_fields = ("brand_name", "brand_email", "campaign_genre")
