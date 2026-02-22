from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import authenticate, logout as auth_logout
from django.contrib.auth import login as auth_login
from django.core.mail import EmailMessage, send_mail
from flygowell import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str as force_text
from . tokens import generate_token
from .forms import InfluencerPlatformConnectionForm
from .models import InfluencerMetricSnapshot, InfluencerPlatformConnection
from .services import (
    ApiIntegrationError,
    fetch_facebook_insights,
    fetch_google_analytics,
    fetch_instagram_insights,
    fetch_youtube_insights,
)
# Create your views here.
def index(request):
    influencers = [
        {"name": "Aarav Menon", "image": "assets/img/team/team-1.jpg"},
        {"name": "Nisha Kapoor", "image": "assets/img/team/team-2.jpg"},
        {"name": "Reyansh Patel", "image": "assets/img/team/team-3.jpg"},
        {"name": "Sara Ali", "image": "assets/img/team/team-4.jpg"},
    ]
    return render(request, "authentication/index.html", {"influencers": influencers})
def home(request):
    return render(request, "authentication/home.html")
def about(request):
    return render(request, "authentication/about.html")
def services(request):
    return render(request, "authentication/services.html")
# def contact(request):
#     return render(request, "authentication/contact.html")

def signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')
        if User.objects.filter(username=username):
            messages.error(request, "Username already exist! Please try some other username.")
            return redirect('index')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email Already Registered!!")
            return redirect('index')
        
        if len(username)>20:
            messages.error(request, "Username must be under 20 charcters!!")
            return redirect('index')
        
        if pass1 != pass2:
            messages.error(request, "Passwords didn't matched!!")
            return redirect('index')
        
        if not username.isalnum():
            messages.error(request, "Username must be Alpha-Numeric!!")
            return redirect('index')

        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active = False
        myuser.save()
        messages.success(request, "Your account has been successfully created. Please check your mail to confirm your email address.")
         # Welcome Email
        subject = "Welcome to True Collabs Login!!"
        message = "Hello " + myuser.first_name + "!! \n" + "Welcome to True Collabs!! \nThank you for visiting our website\n. We have also sent you a confirmation email, please confirm your email address. \n\nThanking You\nHaseeb Ur Rehman (CEO)"        
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)

        #Email confirmation code by S.L.Hussain
        current_site = get_current_site(request)
        email_subject = "Confirm your Email @ TrueCollabs!"
        message2 = render_to_string('email_confirmation.html',{
            
            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser)
        })
        email = EmailMessage(
        email_subject,
        message2,
        settings.EMAIL_HOST_USER,
        [myuser.email],
        )
        email.fail_silently = True
        email.send()
        return redirect('login')
    else:
         return render(request, "authentication/signup.html")

def activate(request,uidb64,token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active = True
        User.profile.signup_confirmation = True
        myuser.save()
        auth_login(request,myuser)
        messages.success(request, "Your Account has been activated!!")
        return redirect('login')
    else:
        return render(request,'authentication/activation_failed.html')    


# authentication/views.py
from django.utils import timezone
from datetime import timedelta
from .utils import send_otp_email

def login(request):
    if request.method == 'POST':
        identifier = request.POST.get('identifier')
        password   = request.POST.get('pass1')

        # find User by email or username
        try:
            user_obj = User.objects.get(email=identifier)
            username = user_obj.username
        except User.DoesNotExist:
            username = identifier

        user = authenticate(request, username=username, password=password)
        if user:
            # generate + email OTP, save to session
            send_otp_email(request, user)
            return redirect('verify_otp')
        messages.error(request, "Invalid credentials")
        return redirect('login')

    return render(request, "authentication/login.html")


# authentication/views.py
from django.contrib.auth import login as auth_login

def verify_otp(request):
    if request.method == 'POST':
        entered = request.POST.get('otp_code')
        sess    = request.session

        # basic expiration + match check
        if 'otp_code' not in sess:
            messages.error(request, "Session expired; please log in again.")
            return redirect('login')

        expires = timezone.fromtimestamp(sess['otp_expires'])
        if timezone.now() > expires:
            messages.error(request, "OTP expired; please log in again.")
            return redirect('login')

        if entered == sess.get('otp_code'):
            # all good → log them in
            user = User.objects.get(pk=sess['otp_user_pk'])
            auth_login(request, user)

            # clean up session
            for k in ('otp_user_pk','otp_code','otp_expires'):
                sess.pop(k, None)

            return redirect('home')
        else:
            messages.error(request, "Wrong code.")
            return redirect('verify_otp')

    return render(request, "authentication/verify_otp.html")

def logout(request):
    auth_logout(request)
    messages.success(request, "Logged Out Successfully!!")
    return redirect('index')
def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        auth_login(request, myuser)
        return redirect('index')
    else:
        return render(request, 'activation_failed.html')


@login_required
def influencer_insights(request):
    if request.method == "POST":
        form = InfluencerPlatformConnectionForm(request.POST)
        if form.is_valid():
            connection = form.save(commit=False)
            connection.influencer = request.user
            connection.save()
            messages.success(request, "Account connected successfully. Sync to fetch live metrics.")
            return redirect("influencer_insights")
    else:
        form = InfluencerPlatformConnectionForm()

    connections = request.user.platform_connections.order_by("-updated_at")
    latest_by_connection = []
    for connection in connections:
        snapshot = connection.snapshots.first()
        latest_by_connection.append({"connection": connection, "snapshot": snapshot})

    return render(
        request,
        "authentication/influencer_insights.html",
        {
            "form": form,
            "connections_with_latest": latest_by_connection,
        },
    )


@login_required
def sync_influencer_metrics(request, connection_id):
    connection = InfluencerPlatformConnection.objects.filter(
        id=connection_id,
        influencer=request.user,
    ).first()
    if not connection:
        messages.error(request, "Connection not found.")
        return redirect("influencer_insights")

    try:
        if connection.platform == InfluencerPlatformConnection.PLATFORM_FACEBOOK:
            payload = fetch_facebook_insights(connection)
        elif connection.platform == InfluencerPlatformConnection.PLATFORM_INSTAGRAM:
            payload = fetch_instagram_insights(connection)
        elif connection.platform == InfluencerPlatformConnection.PLATFORM_YOUTUBE:
            payload = fetch_youtube_insights(connection)
        else:
            payload = fetch_google_analytics(connection)

        followers = payload.get("followers", 0)
        connection.latest_followers = followers
        connection.creator_tier = InfluencerPlatformConnection.resolve_creator_tier(followers)
        connection.save(update_fields=["latest_followers", "creator_tier", "updated_at"])

        snapshot = InfluencerMetricSnapshot.objects.create(
            influencer=request.user,
            connection=connection,
            source=connection.platform,
            followers=followers,
            profile_views=payload.get("profile_views", 0),
            reach=payload.get("reach", 0),
            impressions=payload.get("impressions", 0),
            page_views=payload.get("page_views", 0),
            engagement=payload.get("engagement", 0),
            engagement_rate=payload.get("engagement_rate", 0),
            location=payload.get("location", ""),
            gender_split=payload.get("gender_split", {}),
            city_split=payload.get("city_split", {}),
            raw_payload=payload.get("raw_payload", {}),
        )
        messages.success(
            request,
            f"Metrics synced from {snapshot.get_source_display()}. Tier: {connection.get_creator_tier_display()}.",
        )
    except ApiIntegrationError as exc:
        messages.error(request, f"API sync failed: {exc}")

    return redirect("influencer_insights")



# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib.auth.decorators import login_required
# from .models import Campaign, Deliverable
# from django.contrib import messages

# @login_required
# def list_campaigns(request):
#     campaigns = Campaign.objects.all()
#     return render(request, "campaigns/list_campaigns.html", {"campaigns": campaigns})

# @login_required
# def participate_in_campaign(request, campaign_id):
#     campaign = get_object_or_404(Campaign, id=campaign_id)
#     if Deliverable.objects.filter(campaign=campaign, influencer=request.user).exists():
#         messages.warning(request, "You have already participated in this campaign.")
#         return redirect('list_campaigns')

#     Deliverable.objects.create(campaign=campaign, influencer=request.user)
#     messages.success(request, "You have successfully participated in the campaign.")
#     return redirect('list_campaigns')

# @login_required
# def upload_deliverable(request, campaign_id):
#     campaign = get_object_or_404(Campaign, id=campaign_id)
#     deliverable = Deliverable.objects.filter(campaign=campaign, influencer=request.user).first()
#     if not deliverable:
#         messages.error(request, "You are not participating in this campaign.")
#         return redirect('list_campaigns')

#     if request.method == "POST":
#         deliverable_link = request.POST.get("deliverable_link")
#         if deliverable_link:
#             deliverable.deliverable_link = deliverable_link
#             deliverable.save()
#             messages.success(request, "Deliverable uploaded successfully.")
#             return redirect('list_campaigns')

#     return render(request, "campaigns/upload_deliverable.html", {"campaign": campaign, "deliverable": deliverable})
