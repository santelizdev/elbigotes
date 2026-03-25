import pytest
from rest_framework.test import APIClient

from apps.taxonomy.models import Category


@pytest.mark.django_db
def test_public_category_list_only_returns_active_categories():
    client = APIClient()
    Category.objects.create(name="Veterinarias", slug="veterinarias", is_active=True, sort_order=1)
    Category.objects.create(name="Oculta", slug="oculta", is_active=False, sort_order=2)

    response = client.get("/api/v1/taxonomy/categories/")

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["slug"] == "veterinarias"
