from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def paginationStore(request, projects, results):
    # using Paginator, request in URL already have page no.
    page = request.GET.get('page')
    paginator = Paginator(projects, results)

    # resets results to load page variable number
    try:
        projects = paginator.page(page)
    # if this is just click visit with no page no. given
    except PageNotAnInteger:
        page = 1
        projects = paginator.page(page)
    # if page called is out of range
    except EmptyPage:
        # num_pages tells how many pages ie, set to last page
        page = paginator.num_pages
        projects = paginator.page(page)

    # if we have lots of pages but don't want to show all the buttons in paginator
    leftIndex = (int(page) - 2)
    # nearing initial pages
    if leftIndex < 1:
        leftIndex = 1

    rightIndex = (int(page) + 2)
    # for nearing last pages
    if rightIndex > paginator.num_pages:
        rightIndex = paginator.num_pages + 1

    custom_range = range(leftIndex, rightIndex)

    return custom_range, projects