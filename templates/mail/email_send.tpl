{% extends "mail_templated/base.tpl" %}

{% block body %}
    <p>Dear {{ first_name }},</p>
    <p>Your verification code is: {{ verification_code }}</p>
    <p>Please go back to the registration page and input this code to verify your email address.</p>
    <p>Thank you!</p>
{% endblock %}

