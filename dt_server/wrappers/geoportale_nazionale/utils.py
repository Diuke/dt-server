import api.models as dt_server_models

def build_geoportale_dtm_service_url(layer: dt_server_models.Layer, params):
    base_url = layer.service_url
    url = base_url + "&"
    url += "SERVICE=WMS&"
    url += "VERSION=1.3.0&"
    url += "REQUEST=GetFeatureInfo&"
    url += "FORMAT=image/png&"
    url += "TRANSPARENT=true&"
    url += "QUERY_LAYERS=" + layer.layer_name + "&"
    url += "TILED=true&"
    url += "LAYERS=" + layer.layer_name + "&"
    url += "BBOX=" + params["bbox"] + "&"
    url += "CRS=EPSG:3857&"
    url += "INFO_FORMAT=text/plain&"
    url += "I=0&J=0&WIDTH=1&HEIGHT=1&STYLES="
    return url