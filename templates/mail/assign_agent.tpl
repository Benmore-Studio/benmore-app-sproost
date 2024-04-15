{% extends "mail_templated/base.tpl" %}

{% block subject %}
Action Required: Add Property to Your Dashboard, {{ first_name }}!
{% endblock %}

{% block body %}
Hello {{ first_name }},

You have been assigned a new property with the following unique identifier: 

Property UUID: {{ uuid }}

Please add this UUID to your property list in your dashboard. To do so, log in to your dashboard and navigate to the property add section. Enter the UUID in the designated field to update your property list.


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

  <p>You have been assigned a new property with the following unique identifier:</p>

  <p><strong>Property UUID: {{ uuid }}</strong></p>

  <p>Please add this UUID to your property list in your dashboard. To do so, log in to your <a href="{{base_url}}">Dashboard</a> and navigate to the property add section. Enter the UUID in the designated field to update your property list.</p>

  <p>Should you have any questions or require further assistance, please don't hesitate to get in touch.</p>

  <p>Thank you for your attention to this matter.</p>

  <p>Best regards,<br>
  The Team</p>
</body>
</html>
{% endblock %}
