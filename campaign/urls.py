from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_campaigns, name='list_campaigns'),  # List all campaigns
    path('<int:campaign_id>/participate/', views.participate_in_campaign, name='participate_in_campaign'),
    path('<int:campaign_id>/upload/', views.upload_deliverable, name='upload_deliverable'),
    path('contact-us/', views.contact_us, name='contact_us'),
]
