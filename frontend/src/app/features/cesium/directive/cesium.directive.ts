import { Directive, ElementRef, OnInit } from '@angular/core';

@Directive({
  selector: '[cesium3D]'
})
export class CesiumDirective implements OnInit {

  constructor(private el: ElementRef) { }

  ngOnInit(): void {
    const viewer = new Cesium.Viewer(this.el.nativeElement);
    
  }

}
