from django_ratelimit.decorators import ratelimit
from django.core.cache import cache
from django.http import HttpResponse

@ratelimit(key='ip', rate='5/m', block=False)
def login_view(request):
    if getattr(request, "limited", False):
        ip = request.META.get("REMOTE_ADDR")
        cache.set(f"blocked:{ip}", True, 300)
        return HttpResponse("Too many attempts. You are blocked for 5 minutes.", status=429)

    return HttpResponse("Login page")