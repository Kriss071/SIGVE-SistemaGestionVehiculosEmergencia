def active_page(request):
    if request.resolver_match:
        return {"active_page": request.resolver_match.url_name}
    return {}
