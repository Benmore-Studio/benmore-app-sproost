from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags

        # Send the invitation email containing the referral code and link
def send_invitation_email(email, invitation_code):
    subject  = "You're invited to join our platform as an agent"
    from_email = None
    recipient_list = [email]

    html_content = render_to_string('email/invitation_email.html', {
         'invitation_code': invitation_code,
         'domain_name': settings.DOMAIN_NAME
    })
    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
    email.attach_alternative(html_content, "text/html")
    email.send()
    
