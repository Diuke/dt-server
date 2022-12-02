import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { Map3dComponent } from './features/cesium/map3d/map3d.component';
import { MapComponent } from './features/map/pages/map/map.component';

const routes: Routes = [
  {
    path: '', component: MapComponent
  },

  {
    path: 'cesium', component: Map3dComponent
  }

];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
