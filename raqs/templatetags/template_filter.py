from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, "Aguardando Teste")  # Default to "Aguardando Teste" if key is not found
