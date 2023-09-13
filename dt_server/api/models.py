from django.utils.translation import gettext_lazy as _
from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=256)
    #parent_layer_group = models.ForeignKey("self", blank=True, null=True, on_delete=models.PROTECT, default=None, related_name="children_layer_groups")

    def __str__(self):
        return self.name

    class Meta:
        db_table = "category"
        verbose_name = "Category"
        verbose_name_plural = "Categories"

class LayerService(models.Model):
    class ServiceType(models.TextChoices):
        WFS = 'WFS', _('WFS')
        WMS = 'WMS', _('WMS')
        WMST = 'WMST', _('WMST')
        WCS = 'WCS', _('WCS')
        ARCGIS_ImageServer = 'ARCGIS_IS', _('ArcGIS ImageServer')
        ARCGIS_MapServer = 'ARCGIS_MS', _('ArcGIS MapServer')

    service_type = models.CharField(max_length=256, choices=ServiceType.choices)
    url = models.TextField(null=True)
    wrapper_name = models.CharField(max_length=256, null=False) #this is the name of the wrapper folder 

    layer = models.ForeignKey(
        "Layer",
        related_name="layer_services",
        on_delete=models.CASCADE
    )

class Layer(models.Model):
    source = models.TextField(null=True) # put the source of the layer, i.e., Copernicus, WorldPop, etc.
    layer_name = models.CharField(max_length=256, null=True) #this is the id(s) of the layer(s) in the service
    verbose_name = models.CharField(max_length=256, default="") #Readable name
    abstract = models.TextField(default="") 
    keywords = models.TextField(default="", blank=True, null=True) # Comma separated keywords
    parameters = models.TextField(default="", blank=True) # Comma separated parameters of the layer. Also called dimensions
    category = models.ForeignKey(Category, null=True, on_delete=models.PROTECT, related_name="layers")
    frequency = models.CharField(max_length=256, blank=True, null=True, default="") #monthly, daily, hourly
    units = models.CharField(max_length=100, blank=True, null=True, default="") #units for the values of the layer

    enabled = models.BooleanField(default=True) #appears in searches

    initial_time_range = models.DateField(blank=True, null=True) #DD-MM-AAAA
    final_time_range = models.DateField(blank=True, null=True) #DD-MM-AAAA

    def __str__(self):
        return f'{self.source}: {self.verbose_name} ({self.layer_name})'

    class Meta:
        db_table = "layer"
        verbose_name = "Layer"
        verbose_name_plural = "Layers" 

class Scenario(models.Model):
    name = models.CharField(max_length=256)
    scenario_json = models.JSONField()
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="scenarios")

    def __str__(self):
        return self.name

    class Meta:
        db_table = "scenario"
        verbose_name = "Scenario"
        verbose_name_plural = "Scenarios"