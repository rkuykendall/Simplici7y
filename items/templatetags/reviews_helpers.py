from django import template

register = template.Library()


@register.filter
def stars(rating):
    width = int(rating * 25)
    return f'<ul class="star-rating"><li class="current-rating" style="width:{width}px;">Currently {rating}/5 Stars.</li></ul>'
