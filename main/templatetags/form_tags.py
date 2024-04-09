from django import template

register = template.Library()

@register.filter(name='addattrs')
def addattrs(field, attrs):
    attrs_dict = {attr: value for attr, value in (attr.split('=') for attr in attrs.split(','))}
    return field.as_widget(attrs=attrs_dict)