from django.shortcuts import render
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
# Create your views here.
def index(request):
    return render(request, "authentication/index.html")
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


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']
        user = authenticate(username=username, password=pass1)
        if user is not None:
            auth_login(request, user)
            fname= user.first_name
            return render(request,"authentication/index.html", {'fname': fname})
        else:
            messages.error(request,"Bad Credentials")
            return redirect('index')
        
    return render(request, "authentication/login.html")

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
