import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpModule, JsonpModule } from '@angular/http';

import { routes } from './app.router';

import { LoginService } from './login.service';
import { ImagesService } from './images.service';
import { ImageDetailService } from './image-detail.service';

import { AppComponent } from './app.component';
import { NavbarComponent } from './navbar/navbar.component';
import { ImagesComponent } from './images/images.component';
import { ImageDetailComponent } from './image-detail/image-detail.component';

@NgModule({
  declarations: [
    AppComponent,
    NavbarComponent,
    ImagesComponent,
    ImageDetailComponent
  ],
  imports: [
    BrowserModule,
    HttpModule,
    JsonpModule,
    routes
  ],
  providers: [LoginService, ImagesService, ImageDetailService],
  bootstrap: [AppComponent]
})
export class AppModule { }
