from django.http import HttpResponsePermanentRedirect
from urllib.parse import urlencode
from django.shortcuts import redirect
from django.urls import resolve


class RemoveWwwAndHttpsRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
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
                return HttpResponsePermanentRedirect(new_url)

        return self.get_response(request)


class ValidateQueryParamsMiddleware:
    VALID_QUERY_PARAMS = {
        "home": ["order", "search", "page"],
        "user": ["order", "search", "page"],
        "tag": ["order", "search", "page"],
        "scenario": ["order", "search", "page"],
    }

    ORDER_VALUES = ["old", "reviews", "best", "worst", "loud", "popular"]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            view_name = resolve(request.path_info).view_name
        except:
            view_name = None

        if view_name in self.VALID_QUERY_PARAMS:
            params = request.GET.copy()
            valid_params = self.VALID_QUERY_PARAMS[view_name]
            invalid_params = []

            # Check for invalid parameters
            for param, values in params.lists():
                if param not in valid_params or len(values) > 1 or not any(values):
                    invalid_params.append(param)
                elif param == "order" and values[0] not in self.ORDER_VALUES:
                    invalid_params.append(param)

            # Remove invalid parameters and redirect
            if invalid_params:
                for param in invalid_params:
                    del params[param]

                url = f"{request.path}?{urlencode(params, doseq=True)}"
                return redirect(url)

        response = self.get_response(request)
        return response
