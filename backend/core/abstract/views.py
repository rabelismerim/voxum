from django.http import Http404
from drf_yasg.inspectors import SwaggerAutoSchema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomSchema(SwaggerAutoSchema):
    pass


class AbstractViewApi(GenericAPIView):
    model = None
    model_query = None
    many = None
    pagination = False
    responses = {}
    query_params = ()
    layout_serializers = {}
    schema = CustomSchema

    def get_serializer_class(self):
        method = self.request.method.lower()
        return (
            self.layout_serializers.get(method)
            or self.layout_serializers.get('default')
            or self.serializer_class
        )

    def get_queryset(self):
        if self.model_query is not None:
            queryset = self.model_query
        elif self.model is not None:
            queryset = self.model.objects.all()
        else:
            serializer_model = self.get_serializer_class().Meta.model
            queryset = serializer_model.objects.all()

        return self.filter(self.kwargs.get('id'), **self.kwargs)

    def filter(self, id_=None, **kwargs):
        queryset = self.model_query
        if queryset is None:
            model = self.model or self.get_serializer_class().Meta.model
            queryset = model.objects.all()

        filters = {}
        if id_ is not None:
            filters['id'] = id_
        for parameter in self.query_params:
            name = parameter.get('name')
            field = parameter.get('field', name)
            value = self.request.query_params.get(name)
            if value is not None:
                filters[field] = value.split(',') if field.endswith('__in') else value
        for key, value in kwargs.items():
            if key != 'id' and value is not None:
                filters[key] = value
        return queryset.filter(**filters)

    def get_exclude_values(self):
        return ()

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        is_many = self.many if self.many is not None else 'id' not in kwargs
        if is_many:
            if self.pagination:
                page = self.paginate_queryset(queryset)
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

        instance = queryset.first()
        if instance is None:
            raise Http404
        return Response(self.get_serializer(instance).data)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(
            self.get_serializer(instance).data,
            status=status.HTTP_201_CREATED,
        )

    def put(self, request, *args, **kwargs):
        instance = self.get_queryset().first()
        if instance is None:
            raise Http404
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data if serializer.save() is None else self.get_serializer(serializer.instance).data)

    def patch(self, request, *args, **kwargs):
        instance = self.get_queryset().first()
        if instance is None:
            raise Http404
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        instance = self.get_queryset().first()
        if instance is None:
            raise Http404
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def paginate_queryset(self, queryset):
        paginator = PageNumberPagination()
        paginator.page_size = 50
        return paginator.paginate_queryset(queryset, self.request, view=self)

    def get_paginated_response(self, data):
        paginator = PageNumberPagination()
        paginator.page_size = 50
        page = paginator.paginate_queryset(self.get_queryset(), self.request, view=self)
        if page is None:
            return Response(data)
        return paginator.get_paginated_response(data)
