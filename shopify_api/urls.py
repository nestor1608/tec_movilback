from django.urls import path
from .views import ProductListGraphQLView

urlpatterns = [
    path('products/', ProductListGraphQLView.as_view()),
]