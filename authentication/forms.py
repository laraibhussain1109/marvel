from django import forms

from .models import InfluencerPlatformConnection


class InfluencerPlatformConnectionForm(forms.ModelForm):
    class Meta:
        model = InfluencerPlatformConnection
        fields = ["platform", "external_account_id", "access_token", "refresh_token"]
        widgets = {
            "access_token": forms.Textarea(attrs={"rows": 3}),
            "refresh_token": forms.Textarea(attrs={"rows": 2}),
        }
