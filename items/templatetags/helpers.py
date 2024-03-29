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
    search = context["request"].GET.get("search")

    if view.view_name in ["home", "items"]:
        subtitle = "Downloads"
        if not order:
            subtitle = "Latest Downloads"
    elif view.view_name == "scenario":
        subtitle = f"Downloads for {context['scenario'].name}"
    elif view.view_name == "tag":
        subtitle = f"Tagged '{context['tag'].name.capitalize()}'"
    if order:
        subtitle += order_name(order)
    if search:
        subtitle += f" matching '{search}'"

    return subtitle


@register.simple_tag(takes_context=True)
def pagetitle(context):
    prefix = "Marathon Aleph One Downloads"

    try:
        view = resolve(context["request"].path_info)
    except Resolver404:
        return "Page not found"  # Default title for unmatched paths

    if context["request"].path == "/" and not context["request"].GET:
        return prefix

    if "item" in context:
        return f'Download {context["item"].name} by {context["item"].get_byline()}'

    if view.view_name == "user" and "show_user" in context:
        return f'{prefix} and Reviews from {context["show_user"].first_name}'

    if view.view_name == "tag":
        return f'{prefix} Tagged "{context["tag"].name.capitalize()}"'

    if view.view_name == "scenario":
        return f'{prefix} for {context["scenario"].name}'

    if view.view_name == "users":
        return "Active members of the Marathon Aleph One community"

    if view.view_name == "review_detail":
        return f'Review by {context["review"].user.first_name} for {context["review"].version.item.name}'

    items_subtitle = subtitle(context)
    if items_subtitle:
        return items_subtitle

    return view.view_name.capitalize().replace("_", " ")


@register.simple_tag(takes_context=True)
def description(context):
    max_length = 170
    view = resolve(context["request"].path_info)

    def from_markdown(input):
        single_line_text = re.sub("\s+", " ", strip_tags(markdown.markdown(input)))
        if len(single_line_text) > max_length + 20:
            single_line_text = single_line_text[: max_length - 3] + "..."

        return single_line_text

    if view.view_name == "item_detail" and "item" in context:
        return from_markdown(context["item"].body)

    if view.view_name == "user" and "show_user" in context:
        show_user = context["show_user"]
        return (
            f"{show_user.first_name} is a member of the Marathon Aleph One community with "
            + f"{show_user.items_count} uploads and {show_user.reviews_count} reviews."
        )

    if view.view_name == "review_detail" and "review" in context:
        return from_markdown(context["review"].body)

    return (
        "File sharing downloads for the Marathon Aleph One community."
        + " Download community created maps, scenarios, mods, scripts, and applications."
    )


@register.simple_tag(takes_context=True)
def og_image(context):
    view = resolve(context["request"].path_info)

    if (
        view.view_name == "item_detail"
        and "screenshots" in context
        and len(context["screenshots"]) > 0
    ):
        return context["screenshots"][0].file_content.url

    return None


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
    elif txt == "random":
        name = " ordered randomly"
    return name
