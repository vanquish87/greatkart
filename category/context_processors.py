from .models import Category

# it returns the dictionary of all the objects from model
def menu_links(reqest):
    links = Category.objects.all()

    return dict(links=links)