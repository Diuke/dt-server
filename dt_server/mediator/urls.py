from django.urls import path
from mediator import views as dt_server_views

urlpatterns = [
    path('get-data', dt_server_views.get_data, name='get_layer_data'),    
    path('list-parameter-values/<str:layer_id>/<str:parameter>', dt_server_views.get_list_of_parameter_values, name='categories_hierarchy'),    

    path('update-layers', dt_server_views.update_layers, name='update_layers')
]