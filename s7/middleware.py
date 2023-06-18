from django.http import HttpResponsePermanentRedirect


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
