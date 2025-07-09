from django.http import JsonResponse
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


@csrf_exempt
@require_http_methods(["GET"])
def upload_progress(request, progress_id):
    """
    API endpoint to check upload progress.
    """
    progress = cache.get(
        f"upload_progress_{progress_id}", {"uploaded": 0, "total": 0, "percent": 0}
    )

    return JsonResponse(progress)
