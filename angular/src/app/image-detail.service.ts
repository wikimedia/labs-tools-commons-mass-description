import { Injectable } from '@angular/core';
import { Http, Response } from '@angular/http';
import 'rxjs/add/operator/map';

@Injectable()
export class ImageDetailService {

  constructor(private _http: Http) { }

  private _url = "https://tools.wmflabs.org/commons-mass-description/api-imageinfo?title=";
  
  getImages(image) {
    return this._http.get(this._url + image)
    .map((response:Response) => response.json());
  }

}
