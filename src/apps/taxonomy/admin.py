from django.contrib import admin

from apps.taxonomy.models import Category, Subcategory


class SubcategoryInline(admin.TabularInline):
    model = Subcategory
    extra = 0
    fields = ("name", "slug", "is_active", "sort_order")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "sort_order")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [SubcategoryInline]


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "is_active", "sort_order")
    list_filter = ("is_active", "category")
    search_fields = ("name", "slug", "category__name")
    autocomplete_fields = ("category",)
    prepopulated_fields = {"slug": ("name",)}

