import { ModuleWithProviders } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';


import { AppComponent } from './app.component';
import { ImagesComponent } from './images/images.component';
import { ImageDetailComponent } from './image-detail/image-detail.component';

export const router: Routes = [
  { path: '', redirectTo: 'home', pathMatch: 'full' },
  { path: 'image/:imgname', component: ImageDetailComponent},
  { path: 'home', component: ImagesComponent},
  { path: '**', component: ImagesComponent}
];

export const routes: ModuleWithProviders = RouterModule.forRoot(router);