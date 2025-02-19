from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Campaign, Deliverable
from django.contrib import messages

@login_required
def list_campaigns(request):
    campaigns = Campaign.objects.all()
    return render(request, "campaigns/list_campaigns.html", {"campaigns": campaigns})

@login_required
def participate_in_campaign(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)
    if Deliverable.objects.filter(campaign=campaign, influencer=request.user).exists():
        messages.warning(request, "You have already participated in this campaign.")
        return redirect('list_campaigns')

    Deliverable.objects.create(campaign=campaign, influencer=request.user)
    messages.success(request, "You have successfully participated in the campaign.")
    return redirect('list_campaigns')

@login_required
def upload_deliverable(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)
    deliverable = Deliverable.objects.filter(campaign=campaign, influencer=request.user).first()
    if not deliverable:
        messages.error(request, "You are not participating in this campaign.")
        return redirect('list_campaigns')

    if request.method == "POST":
        deliverable_link = request.POST.get("deliverable_link")
        if deliverable_link:
            deliverable.deliverable_link = deliverable_link
            deliverable.save()
            messages.success(request, "Deliverable uploaded successfully.")
            return redirect('list_campaigns')

    return render(request, "campaigns/upload_deliverable.html", {"campaign": campaign, "deliverable": deliverable})

from django.shortcuts import render, redirect
from .forms import CampaignInquiryForm

def contact_us(request):
    if request.method == 'POST':
        form = CampaignInquiryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Submission successful! Our team will contact you soon with the email and password.")
            return redirect('index')  # Redirect to a success page
    else:
        form = CampaignInquiryForm()
    return render(request, 'campaigns/contact_us.html', {'form': form})