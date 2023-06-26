import re
import markdown

from django.utils.html import strip_tags
from django import template
from django.urls import resolve, Resolver404

register = template.Library()


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    query = context["request"].GET.copy()

    # Here we ensure that we replace existing values instead of adding to them
    for key, value in kwargs.items():
        query[key] = value

    return query.urlencode()


@register.simple_tag(takes_context=True)
def subtitle(context):
    subtitle = ""
    view = resolve(context["request"].path_info)
    order = context["request"].GET.get("order")

    if view.view_name in ["home", "items"]:
        subtitle = "Items"
        if not order:
            subtitle = "Latest Updates and Submissions"
    elif view.view_name == "scenario":
        subtitle = context["scenario"].name
    elif view.view_name == "tag":
        subtitle = f"Tagged '{context['tag'].name.capitalize()}'"
    if order:
        subtitle += order_name(order)

    return subtitle


@register.simple_tag(takes_context=True)
def pagetitle(context):
    try:
        view = resolve(context["request"].path_info)
    except Resolver404:
        return "Page not found"  # Default title for unmatched paths

    if context["request"].path == "/":
        return "Marathon Aleph One community downloads."

    if "item" in context:
        return f'{context["item"].name} by {context["item"].user.first_name}'

    if view.view_name == "user" and "show_user" in context:
        return context["show_user"].first_name

    items_subtitle = subtitle(context)
    if items_subtitle:
        return items_subtitle

    return view.view_name.capitalize().replace("_", " ")


@register.simple_tag(takes_context=True)
def description(context):
    max_length = 170
    view = resolve(context["request"].path_info)

    if view.view_name == "item_detail" and "item" in context:
        body = re.sub("\s+", " ", strip_tags(markdown.markdown(context["item"].body)))
        if len(body) > max_length + 20:
            body = body[: max_length - 3] + "..."

        return body

    if view.view_name == "user" and "show_user" in context:
        show_user = context["show_user"]
        return (
            f"{show_user.first_name} is a member of the Marathon Aleph One community with "
            + f"{show_user.items_count} uploads and {show_user.reviews_count} reviews."
        )

    return (
        "File sharing downloads for the Marathon Aleph One community."
        + " Download community created maps, scenarios, mods, scripts, and applications."
    )


def order_name(txt):
    name = " by "
    if txt == "new":
        name += "Latest Updates"
    elif txt == "old":
        name += "Oldest Updates"
    elif txt == "reviews":
        name += "Average Reviews"
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
