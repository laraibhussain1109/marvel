from django.utils import timezone
from datetime import timedelta
import time
import random
from django.core.mail import send_mail
from django.conf import settings

def send_otp_email(request, user):
    code = f"{random.randint(0, 999999):06d}"
    subject = "Your marvel Collabs login code"
    message = (
        f"Hi {user.first_name},\n\n"
        f"Your one‑time login code is: {code}\n\n"
        "This code will expire in 5 minutes.\n\n"
        "If you didn’t request this, please ignore."
    )
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)

    # store in session
    request.session['otp_user_pk'] = user.pk
    request.session['otp_code']    = code
    request.session['otp_expires'] = time.time()+5*60
