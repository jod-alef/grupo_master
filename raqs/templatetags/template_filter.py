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
