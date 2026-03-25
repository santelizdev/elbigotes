from django.urls import path

from apps.taxonomy.api.views import PublicCategoryListView

urlpatterns = [
    path("categories/", PublicCategoryListView.as_view(), name="taxonomy-public-categories"),
]
