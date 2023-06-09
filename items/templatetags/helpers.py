from django import template
from django.urls import resolve
from django.utils.safestring import mark_safe
from markdown import markdown

from items.models import Item

register = template.Library()


# @register.filter
# def format(text):
#     if text:
#         text = text.replace("<", "&lt;").replace(">", "&gt;")
#         return mark_safe(markdown(text))
#     return text


# @register.filter
# def clean(text):
#     if text:
#         text = text.replace("<", "&lt;").replace(">", "&gt;")
#     return text


@register.simple_tag(takes_context=True)
def pagetitle(context, text):
    view = resolve(context["request"].path_info)
    if view.view_name == "items":
        if text == "Marathon":
            text = f"Marathon {text}"
    if context["request"].path == "/":
        text = "Marathon Aleph One community downloads."
    return text


@register.simple_tag(takes_context=True)
def subtitle(context):
    subtitle = ""  # Initialize subtitle
    view = resolve(context["request"].path_info)
    order = context["request"].GET.get("order")

    if view.view_name in ["home", "items"]:
        subtitle = "Items"
        if not order:
            subtitle = "Latest Updates and Submissions"
    elif view.view_name == "item":
        # assuming permalink is a slug
        subtitle = Item.objects.get(permalink=context["id"]).name
    elif view.view_name == "tag":
        subtitle = f"Tagged '{context['id'].capitalize()}'"
    if order:
        subtitle += order_name(order)

    return subtitle


def order_name(txt):
    name = " by "
    if txt == "new":
        name += "Latest Updates"
    elif txt == "old":
        name += "Oldest Updates"
    elif txt == "best":
        name += "Best Reviewed"
    elif txt == "worst":
        name = ""
    elif txt == "popular":
        name += "Most Downloads"
    elif txt == "unpopular":
        name += "Fewest Downloads"
    # elif txt == "day":
    #     name += "Daily Downloads"
    # elif txt == "week":
    #     name += "Weekly Downloads"
    # elif txt == "month":
    #     name += "Monthly Downloads"
    elif txt == "loud":
        name += "Most Reviews"
    elif txt == "quiet":
        name += "Fewest Reviews"
    return name
