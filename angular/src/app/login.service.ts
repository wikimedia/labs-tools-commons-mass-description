import { Injectable } from '@angular/core';
import { Http, Response } from '@angular/http';
import 'rxjs/add/operator/map';

@Injectable()
export class LoginService {

  constructor(private _http: Http) { 
    this.isLogged();
  }

  private _url = "https://tools.wmflabs.org/commons-mass-description/api-username";

  isLogged() {
    return this._http.get(this._url)
    .map((response:Response) => response.json());
  }

}
