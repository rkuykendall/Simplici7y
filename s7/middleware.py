import re
from django.http import HttpResponsePermanentRedirect
from urllib.parse import urlencode
from django.shortcuts import redirect
from django.urls import resolve


class RemoveWwwAndHttpsRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print('RemoveWwwAndHttpsRedirectMiddleware')
        official_domain = "simplici7y.com"
        host = request.get_host().split(":")[0]
        scheme = request.scheme

        if host.endswith(official_domain):
            if host and host.startswith("www.") or scheme != "https":
                new_host = host[4:] if host.startswith("www.") else host
                new_scheme = "https" if scheme != "https" else scheme
                new_url = "{}://{}{}".format(
                    new_scheme, new_host, request.get_full_path()
                )
                print('new_url', new_url)
                return HttpResponsePermanentRedirect(new_url)

        return self.get_response(request)


class ValidateAndCleanUrlsMiddleware:
    print('ValidateAndCleanUrlsMiddleware')
    VALID_QUERY_PARAMS = {
        "home": ["order", "search", "page"],
        "user": ["order", "search", "page"],
        "tag": ["order", "search", "page"],
        "scenario": ["order", "search", "page"],
        "reviews": ["page"],
    }

    ORDER_VALUES = ["old", "reviews", "best", "worst", "loud", "popular", "random"]

    BAD_URL_REGEX = re.compile(r"{.*")

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        clean_path = self.BAD_URL_REGEX.sub('', request.path_info)

        if request.path_info != clean_path:
            return redirect(clean_path)

        try:
            view_name = resolve(clean_path).view_name
        except:
            view_name = None

        if view_name in self.VALID_QUERY_PARAMS:
            params = request.GET.copy()

            for param in list(params):
                values = params.getlist(param)
                if self._is_valid_param(view_name, param, values):
                    # If there are multiple values, only keep the last one
                    if len(values) > 1:
                        params.setlist(param, [values[-1]])
                else:
                    params.pop(param)

            if request.GET != params:
                url = f"{clean_path}?{urlencode(params, doseq=True)}"
                return redirect(url)

        response = self.get_response(request)
        return response

    def _is_valid_param(self, view_name, param, values):
        if param not in self.VALID_QUERY_PARAMS[view_name]:
            return False

        if param == "order" and values[-1] not in self.ORDER_VALUES:
            return False

        if param == "page" and not values[-1].isdigit():
            return False

        return True
