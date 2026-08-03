from rest_framework.pagination import PageNumberPagination


class StandardPageNumberPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_metadata(self) -> dict[str, int]:
        return {
            'page': self.page.number,
            'page_size': self.page.paginator.per_page,
            'total_items': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'has_next': self.page.has_next(),
            'has_previous': self.page.has_previous(),
        }
