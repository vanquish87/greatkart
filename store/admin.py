from django.contrib import admin
from .models import Product, Variation, ReviewRating, ProductGallery
import admin_thumbnails


# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'product_name',
        'price',
        'stock',
        'category',
        'created_date',
        )
    prepopulated_fields = {
        'slug': ('product_name',)
        }


class VariationAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'variation_category',
        'variation_value',
        'is_active',
        )

    list_editable = (
        'is_active',
    )
    list_filter = (
        'product',
        'variation_category',
        'variation_value',
        )

# @admin_thumbnails is used to preview photo in admin panel
@admin_thumbnails.thumbnail('image')
# this will give tabular unlimited photo upload in admin
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1


admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(ReviewRating)
admin.site.register(ProductGallery)