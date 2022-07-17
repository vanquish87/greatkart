from django.db import models
from django.urls import reverse
from category.models import Category


# Create your models here.
class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=500, blank=True)
    price = models.IntegerField()
    images = models.ImageField(upload_to='photos/products')
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)

    # OnetoMany relationship with category
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    # create Timestamp automatically
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    # alternative way to get a url for this model (needs two args)
    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])

    def __str__(self):
        return self.product_name


# this is for calling variations like size n color directly from
# like product.variation_set.colors
class VariationManager(models.Manager):
    def colors(self):
        return super(
            VariationManager, self
            ).filter(
            variation_category='color',
            is_active=True
            )

    def sizes(self):
        return super(
            VariationManager, self
            ).filter(
            variation_category='size',
            is_active=True
            )


class Variation(models.Model):
    variation_category_choices = (
        ('color', 'coloring'),
        ('size', 'sizing'),
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(
        max_length=100,
        choices=variation_category_choices
        )
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    # create Timestamp automatically
    created_date = models.DateTimeField(auto_now=True)

    # to tell this model that we are using VariationManager to extend it
    objects = VariationManager()

    # since it is not a string
    def __str__(self):
        return self.variation_value
