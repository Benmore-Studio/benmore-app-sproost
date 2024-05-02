{% extends "mail_templated/base.tpl" %}

{% block subject %}
Action Required: Add Property to Your Dashboard, {{ first_name }}!
{% endblock %}

{% block body %}
Hello {{ first_name }},

You have been assigned a new property: 

you can access it on dashboard

Should you have any questions or require further assistance, please don't hesitate to get in touch.

Thank you for your attention to this matter.

Best regards,
The Team
{% endblock %}

{% block html %}
<html>
<head>
  <style>
    /* Add any specific style you want here. */
  </style>
</head>
<body>
  <p>Hello <strong>{{ first_name }}</strong>,</p>

  <p>You can access it on dashboard</p>

  <p>Should you have any questions or require further assistance, please don't hesitate to get in touch.</p>

  <p>Thank you for your attention to this matter.</p>

  <p>Best regards,<br>
  The Team</p>
</body>
</html>
{% endblock %}
