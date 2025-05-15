from django.templatetags.static import static

def user_logo(request):
    if request.user.is_authenticated:
        user = request.user
        if hasattr(user, "client") and user.client and user.client.company_logo:
            return {"logo_url": user.client.company_logo.url}
    return {"logo_url": static("images/Google_2015_logo.svg.webp")}
