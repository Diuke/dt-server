import { Injectable } from '@angular/core';
import { UrlsService } from 'src/app/core/services/urls.service';
import { environment } from 'src/environments/environment';
import Map from 'ol/Map';
import { MapLayerModel } from 'src/app/core/models/mapLayerModel';
import { HttpClient, HttpHeaders } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class MapServiceService {
  BASE_URL = environment.backend_base_url;

  public globalMap: Map | null= null;
  public capturingAnalysisPoint: boolean = false;
  public layerMap: { [id: number]: MapLayerModel } = {};

  constructor(
    private urlsService: UrlsService,
    private http: HttpClient
  ) { }

  setMap(map: Map){
    this.globalMap = map;
  }

  getMap(){
    return this.globalMap;
  }

  getLayerMap(){
    return this.layerMap;
  }

  getLayersWMS(){
    let URL = this.urlsService.buildUrl("layers_wms");
    let headers = new HttpHeaders().set("Api-Key", this.urlsService.getApiKey());
    return this.http.get(URL, {headers: headers});
  }

  getLayersWFS(){
    let URL = this.urlsService.buildUrl("layers_wfs");
    let headers = new HttpHeaders().set("Api-Key", this.urlsService.getApiKey());
    return this.http.get(URL, {headers: headers});
  }

  getLayerHierarchy(start_date: string, end_date: string){
    let URL = this.urlsService.buildUrl("layer_hierarchy");
    if(start_date && end_date){
      URL += "?start_date=" + start_date + "&end_date=" + end_date;
    }
    let headers = new HttpHeaders().set("Api-Key", this.urlsService.getApiKey());
    return this.http.get(URL, {headers: headers});
  }
}
