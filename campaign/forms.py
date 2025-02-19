from django import forms
from .models import CampaignInquiry

class CampaignInquiryForm(forms.ModelForm):
    class Meta:
        model = CampaignInquiry
        fields = [
            'brand_name',
            'brand_email',
            'brand_contact',
            'campaign_genre',
            'sub_genre',
            'budget',
            'target_audience',
            'region',
        ]
        widgets = {
            'brand_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your brand name'}),
            'brand_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
            'brand_contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your contact number'}),
            'campaign_genre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter campaign genre'}),
            'sub_genre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter sub-genre'}),
            'budget': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter budget'}),
            'target_audience': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe your target audience'}),
            'region': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the region'}),
        }
