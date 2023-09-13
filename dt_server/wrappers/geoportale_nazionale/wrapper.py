from geoportale_nazionale import utils as geoportale_utils

def get_data(layer, params):
    url = geoportale_utils.build_geoportale_dtm_service_url(layer, params)
    
    resp_body = {
        "value": 0,
        "units": 0
    }

    return resp_body
