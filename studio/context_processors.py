from django.conf import settings

def product_info(request):
    return {"PRODUCT_NAME": settings.PRODUCT_NAME}
