import pytest

from django.urls import reverse

from thunderstore.core.factories import UserFactory

from ..factories import UploaderIdentityFactory
from ..factories import PackageFactory
from ..factories import PackageVersionFactory


@pytest.mark.django_db
def test_package_list_view(client):
    for i in range(4):
        uploader = UploaderIdentityFactory.create(
            name=f"Tester-{i}",
        )
        package = PackageFactory.create(
            owner=uploader,
            name=f"test_{i}",
            is_active=True,
            is_deprecated=False,
        )
        PackageVersionFactory.create(
            name=package.name,
            package=package,
            is_active=True,
        )
    response = client.get(reverse("packages.list"))
    assert response.status_code == 200

    for i in range(4):
        assert f"test_{i}".encode("utf-8") in response.content


@pytest.mark.django_db
def test_package_detail_view(client, active_package):
    response = client.get(active_package.get_absolute_url())
    assert response.status_code == 200
    response_text = response.content.decode("utf-8")
    assert active_package.name in response_text
    assert active_package.owner.name in response_text


@pytest.mark.django_db
def test_package_detail_version_view(client, active_version):
    response = client.get(active_version.get_absolute_url())
    assert response.status_code == 200
    response_text = response.content.decode("utf-8")
    assert active_version.name in response_text
    assert active_version.owner.name in response_text


def test_package_create_view_not_logged_in(client):
    response = client.get(reverse("packages.create"))
    assert response.status_code == 302


@pytest.mark.django_db
def test_package_create_view_logged_in(client):
    user = UserFactory.create()
    client.force_login(user)
    response = client.get(reverse("packages.create"))
    assert response.status_code == 200
    assert b"Upload package" in response.content
