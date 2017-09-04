import { Component, OnInit } from '@angular/core';
import { LoginService } from '../login.service';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.css']
})
export class NavbarComponent implements OnInit {

  constructor(private _login: LoginService) { }

  login: any = {};

  ngOnInit() {
    this._login.isLogged().subscribe(data => {
      console.log(data);
      this.login = data;
    })
  }

}
