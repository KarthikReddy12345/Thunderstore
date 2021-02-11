from django.db.models import Q
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField, empty

from thunderstore.community.models import PackageCategory, PackageListing
from thunderstore.repository.models import Package, PackageVersion, UploaderIdentity
from thunderstore.repository.package_upload import PackageUploadForm


class PackageVersionSerializerExperimental(serializers.ModelSerializer):
    download_url = SerializerMethodField()
    full_name = SerializerMethodField()
    dependencies = SerializerMethodField()

    def get_download_url(self, instance):
        url = instance.download_url
        if "request" in self.context:
            url = self.context["request"].build_absolute_uri(instance.download_url)
        return url

    def get_full_name(self, instance):
        return instance.full_version_name

    def get_dependencies(self, instance):
        return [
            dependency.full_version_name for dependency in instance.dependencies.all()
        ]

    class Meta:
        model = PackageVersion
        ref_name = "PackageVersionExperimental"
        fields = (
            "name",
            "full_name",
            "description",
            "icon",
            "version_number",
            "dependencies",
            "download_url",
            "downloads",
            "date_created",
            "website_url",
            "is_active",
        )


class PackageSerializerExperimental(serializers.ModelSerializer):
    owner = SerializerMethodField()
    full_name = SerializerMethodField()
    package_url = SerializerMethodField()
    latest = PackageVersionSerializerExperimental()
    total_downloads = SerializerMethodField()

    def get_owner(self, instance):
        return instance.owner.name

    def get_full_name(self, instance):
        return instance.full_package_name

    def get_package_url(self, instance):
        return instance.get_full_url(self.context["community_site"].site)

    def get_total_downloads(self, instance):
        return instance.downloads

    class Meta:
        model = Package
        ref_name = "PackageExperimental"
        fields = (
            "name",
            "full_name",
            "owner",
            "package_url",
            "date_created",
            "date_updated",
            "rating_score",
            "is_pinned",
            "is_deprecated",
            "total_downloads",
            "latest",
        )
        depth = 0


class PackageListingSerializerExperimental(serializers.ModelSerializer):
    package = PackageSerializerExperimental()
    categories = SerializerMethodField()

    def get_categories(self, instance):
        return set(instance.categories.all().values_list("name", flat=True))

    class Meta:
        model = PackageListing
        ref_name = "PackageListingExperimental"
        fields = (
            "package",
            "has_nsfw_content",
            "categories",
        )


class PackageUploadAuthorNameField(serializers.SlugRelatedField):
    """Package upload's author name metadata field."""

    def __init__(self, *args, **kwargs):
        kwargs["slug_field"] = "name"
        super().__init__(*args, **kwargs)

    def get_queryset(self):
        return UploaderIdentity.objects.exclude(
            ~Q(members__user=self.context["request"].user),
        )


class PackageUploadCategoriesField(serializers.RelatedField):
    """Package upload's categories metadata field."""

    def get_queryset(self):
        return PackageCategory.objects.exclude(
            ~Q(community=self.context["request"].community),
        )

    def to_representation(self, value):
        return [c.slug for c in value]

    def to_internal_value(self, data):
        if not isinstance(data, list):
            raise serializers.ValidationError("Not a list")

        categories = self.get_queryset().filter(slug__in=data)
        slugs = set(categories.values_list("slug", flat=True))
        errors = {
            category_slug: f"category not found"
            for category_slug in data
            if category_slug not in slugs
        }
        if errors:
            raise serializers.ValidationError(errors)
        return categories


class JSONSerializerField(serializers.JSONField):
    """Parses a JSON string and passes the data to a Serializer."""

    def __init__(self, serializer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serializer = serializer

    def bind(self, field_name, parent):
        super().bind(field_name, parent)
        self.serializer.bind(field_name, parent)

    def run_validation(self, data=empty):
        return self.serializer.run_validation(super().run_validation(data))


class PackageUploadMetadataSerializer(serializers.Serializer):
    """Non-file fields used for package upload."""

    author_name = PackageUploadAuthorNameField()
    categories = PackageUploadCategoriesField()
    has_nsfw_content = serializers.BooleanField()


class PackageUploadSerializerExperiemental(serializers.Serializer):
    file = serializers.FileField(write_only=True)
    metadata = JSONSerializerField(serializer=PackageUploadMetadataSerializer())

    def _create_form(self, data) -> PackageUploadForm:
        request = self.context["request"]
        metadata = data.get("metadata", {})
        return PackageUploadForm(
            user=request.user,
            identity=metadata.get("author_name"),
            community=request.community,
            data={
                "categories": metadata.get("categories"),
                "has_nsfw_content": metadata.get("has_nsfw_content"),
            },
            files={"file": data.get("file")},
        )

    def validate(self, data):
        form = self._create_form(data)
        if not form.is_valid():
            raise serializers.ValidationError(form.errors)
        return data

    def create(self, validated_data) -> PackageVersion:
        form = self._create_form(validated_data)
        form.is_valid()
        return form.save()
