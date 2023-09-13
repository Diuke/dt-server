export class LayerModel {
    id: number
    layer_name: string
    verbose_name: string
    abstract: string
    keywords: string
    category: {
        id: number,
        name: string
    }
    frequency: string
    units: string
    initial_time_range: string
    final_time_range: string
    parameters: string
    source: string
    services: LayerService[]
}

export class LayerService {
    service_type: string
    url: string
    wrapper_name: string 
}

export class LayerCategory {
    id: number
    layers: LayerModel[]
    name: string
    selected: boolean
}