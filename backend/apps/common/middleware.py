from django.contrib.auth import logout
from django.shortcuts import redirect

from apps.common.admin_scoping import has_active_admin_scope


class AdminScopeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/admin/") and request.path != "/admin/login/":
            if request.user.is_authenticated and not has_active_admin_scope(request):
                logout(request)
                return redirect("staff-login")
        return self.get_response(request)
