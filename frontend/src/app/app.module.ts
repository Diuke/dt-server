import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { CoreModule } from './core/core.module';
import { CesiumDirective } from './features/cesium/directive/cesium.directive';
import { Map3dComponent } from './features/cesium/map3d/map3d.component';

@NgModule({
  declarations: [
    AppComponent,
    CesiumDirective,
    Map3dComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    CoreModule,
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
