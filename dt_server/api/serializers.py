from django.db.models import fields
from rest_framework import serializers
from api import models as dt_server_models

class BasicCategorySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()

    class Meta:
        model = dt_server_models.Category
        fields = "__all__"

class LayerServiceSerializer(serializers.Serializer):
    service_type = serializers.CharField()
    url = serializers.CharField()
    wrapper_name = serializers.CharField()

    class Meta:
        model = dt_server_models.LayerService
        fields = "__all__"

class LayerSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    layer_name = serializers.CharField()
    verbose_name = serializers.CharField()
    abstract = serializers.CharField()
    keywords = serializers.CharField()
    category = BasicCategorySerializer()
    frequency = serializers.CharField()
    initial_time_range = serializers.DateField()
    final_time_range = serializers.DateField()
    parameters = serializers.CharField()
    source = serializers.CharField()
    units = serializers.CharField()
    enabled = serializers.BooleanField()

    services = serializers.SerializerMethodField()

    def get_services(self, obj):
        children_list = obj.layer_services.all()
        return LayerServiceSerializer(children_list, many=True).data

    class Meta:
        model = dt_server_models.Layer
        fields = "__all__"

class CategorySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    layers = serializers.SerializerMethodField()

    def get_layers(self, obj):
        children_list = obj.layers.all()
        return LayerSerializer(children_list, many=True).data

    class Meta:
        model = dt_server_models.Category
        fields = "__all__"

class ScenarioSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    scenario_json = serializers.JSONField()

    class Meta:
        model = dt_server_models.Scenario
        fields = "__all__"