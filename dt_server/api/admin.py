from django.contrib import admin
from api import models

# Register your models here.

class LayerServiceInline(admin.TabularInline):
    model = models.LayerService
    extra=0

@admin.register(models.Layer)
class LayerAdmin(admin.ModelAdmin):
    inlines = [LayerServiceInline]
    



@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    pass