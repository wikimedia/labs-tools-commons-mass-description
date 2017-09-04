import { Component, OnInit } from '@angular/core';
import {Router, ActivatedRoute, Params} from '@angular/router';
import { ImageDetailService } from '../image-detail.service';

@Component({
  selector: 'app-image-detail',
  templateUrl: './image-detail.component.html',
  styleUrls: ['./image-detail.component.css']
})
export class ImageDetailComponent implements OnInit {

  constructor(private _route: ActivatedRoute, private _imageDetail: ImageDetailService) { }

  image: any = [];

  ngOnInit() {
    let image = this._route.snapshot.params['imgname'];
    console.log(image);
    this._imageDetail.getImages(image).subscribe(data => {
      console.log(data);
      this.image = data;
    });
  }

}
