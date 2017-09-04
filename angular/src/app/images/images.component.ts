import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { ImagesService } from '../images.service';

@Component({
  selector: 'app-images',
  templateUrl: './images.component.html',
  styleUrls: ['./images.component.css']
})
export class ImagesComponent implements OnInit {

  constructor(private _router: Router, private _images: ImagesService) { }

  images = [];

  ngOnInit() {
    this._images.getImages().subscribe(data => {
      console.log(data);
      this.images = data;
    })
  }

  onSelect(img){
    this._router.navigate(['/image', img.name]);
  }

}
