from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)  # Return None if key is not found

@register.filter
def split(value, delimiter=','):
    """Split a string by delimiter"""
    if not value:
        return []
    return value.split(delimiter)

@register.filter
def pluralize_pt(value, arg):
    """Custom pluralization filter for Portuguese
    Usage: {{ count|pluralize_pt:"singular,plural" }}
    """
    try:
        singular, plural = arg.split(',')
        if value == 1:
            return singular
        else:
            return plural
    except (ValueError, AttributeError):
        return arg
