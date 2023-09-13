import datetime
from rest_framework.decorators import api_view, permission_classes
from rest_framework_api_key.permissions import HasAPIKey
from django.db.models import Q
from rest_framework.response import Response
import api.models as dt_server_models
import api.serializers as dte_serializers

@api_view(['GET'])
@permission_classes([HasAPIKey])
def categories(request):
    categories = dt_server_models.Category.objects.all()
    serializer = dte_serializers.BasicCategorySerializer(categories, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([HasAPIKey])
def categories_hierarchy(request):
    start_filter_parameter = request.GET.get('start_date') #AAAA-MM-DD
    end_filter_parameter = request.GET.get('end_date') #YYYY-MM-DD
    if not start_filter_parameter and not end_filter_parameter:
        layer_group_list = dt_server_models.Category.objects.all()
        categories_serialized = dte_serializers.CategorySerializer(layer_group_list, many=True).data
    else:
        start_filter_date_split = start_filter_parameter.split("-")
        end_filter_date_split = end_filter_parameter.split("-")
        
        start_filter_date = datetime.date(int(start_filter_date_split[0]), int(start_filter_date_split[1]), int(start_filter_date_split[2]))
        end_filter_date = datetime.date(int(end_filter_date_split[0]), int(end_filter_date_split[1]), int(end_filter_date_split[2]))

        #initial_time_range, final_time_range
        layer_group_list = dt_server_models.Layer.objects.all().filter(
            (Q(initial_time_range__lte=start_filter_date) & Q(final_time_range__gte=start_filter_date)) |
            (Q(initial_time_range__lte=end_filter_date) & Q(final_time_range__gte=end_filter_date)) |
            (Q(initial_time_range__gte=start_filter_date) & Q(final_time_range__lte=end_filter_date)) |
            (Q(initial_time_range__lte=end_filter_date) & Q(final_time_range=None)) |
            (Q(initial_time_range=None) & Q(final_time_range=None))
        )
        layer_group_list = layer_group_list.filter(enabled=True)
        layer_group_list = layer_group_list.order_by("verbose_name")
        layers_serialized = dte_serializers.LayerSerializer(layer_group_list, many=True).data
        categories_list = dt_server_models.Category.objects.all()
        categories_serialized = dte_serializers.BasicCategorySerializer(categories_list, many=True).data
        
        for category in categories_serialized:
            category["layers"] = []
            for layer in layers_serialized:
                if category is not None:
                    if layer["category"]["id"] == category["id"]:
                        category["layers"].append(layer)

    return Response(categories_serialized)
