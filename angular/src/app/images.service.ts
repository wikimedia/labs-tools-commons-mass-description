import { Injectable } from '@angular/core';
import { Http, Response } from '@angular/http';
import 'rxjs/add/operator/map';

@Injectable()
export class ImagesService {

  constructor(private _http: Http) { 
    this.getImages();
  }

  private _url = "https://tools.wmflabs.org/commons-mass-description/api-images";
  
  getImages() {
    return this._http.get(this._url)
    .map((response:Response) => response.json());
  }
}
