import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable()
export class CsrfInterceptor implements HttpInterceptor {
  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    const csrfReq = req.clone({
      headers: req.headers.set('X-CSRF-Token', 'YOUR_CSRF_TOKEN_HERE')
    });
    return next.handle(csrfReq);
  }
}
