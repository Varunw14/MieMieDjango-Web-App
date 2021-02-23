import django_filters
from django_filters import CharFilter
from .models import Module
from django.db.models import Q

class ModuleFilter(django_filters.FilterSet):
    # Description = CharFilter(field_name='Description', lookup_expr='icontains')
    category = django_filters.CharFilter(method='filter_by_all_name_fields')

    class Meta:
        model = Module
        fields = '__all__'
        filter_fields = fields
        exclude = ['Module_ID', 'Department_ID', 'Catalogue_Link']

        def filter_by_all_name_fields(self, queryset, value):
            return queryset
