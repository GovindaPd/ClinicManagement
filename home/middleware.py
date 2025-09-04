from django_ratelimit import ratelimit
from django.core.cache import cache
from django.http import HttpResponseForbidden


class BlockUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = self.get_client_ip(request)
        # if request.path.startswith("/login/"):  # apply only to login
        #     if LoginAttempt.too_many_attempts(ip):
        #         return JsonResponse({"error": "Too many attempts. Try again later."}, status=429)

        #     # log attempt only for POST requests (actual login tries)
        #     if request.method == "POST":
        #         LoginAttempt.objects.create(ip_address=ip)
        if cache.get(f"blocked:{ip}"):
            return HttpResponseForbidden("You are temporarily blocked due to too many failed attempts.")
        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if not x_forwarded_for:
            x_forwarded_for = request.META.get('HTTP_REFERER')
        return x_forwarded_for



# from django_ratelimit.decorators import ratelimit
# from django.core.cache import cache
# from django.http import HttpResponse

# @ratelimit(key='ip', rate='5/m', block=False)
# def login_view(request):
#     if getattr(request, "limited", False):
#         ip = request.META.get("REMOTE_ADDR")
#         cache.set(f"blocked:{ip}", True, 300)  # block for 5 minutes
#         return HttpResponse("Too many attempts. You are blocked for 5 minutes.", status=429)

#     return HttpResponse("Login page")