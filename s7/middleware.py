from django.http import HttpResponsePermanentRedirect


class RemoveWwwMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(':')[0]
        if host and host.startswith('www.'):
            new_host = host[4:]
            new_url = "{}://{}{}".format(request.scheme, new_host, request.get_full_path())
            return HttpResponsePermanentRedirect(new_url)
        return self.get_response(request)
