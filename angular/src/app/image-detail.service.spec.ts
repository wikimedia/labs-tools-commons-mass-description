import { TestBed, inject } from '@angular/core/testing';

import { ImageDetailService } from './image-detail.service';

describe('ImageDetailService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [ImageDetailService]
    });
  });

  it('should be created', inject([ImageDetailService], (service: ImageDetailService) => {
    expect(service).toBeTruthy();
  }));
});
