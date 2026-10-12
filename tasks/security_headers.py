# tasks/security_headers.py
# Middleware qui ajoute les en-têtes de sécurité manquants repérés par ZAP
# (clickjacking, CSP, Permissions-Policy, COEP/COOP, nosniff, cache).
class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["X-Frame-Options"] = "DENY"
        response["X-Content-Type-Options"] = "nosniff"
        response["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none'"
        response["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response["Cross-Origin-Embedder-Policy"] = "require-corp"
        response["Cross-Origin-Opener-Policy"] = "same-origin"
        response["Cache-Control"] = "no-store"
        return response