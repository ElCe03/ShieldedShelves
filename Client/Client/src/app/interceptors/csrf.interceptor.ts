import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable()
export class CsrfInterceptor implements HttpInterceptor {
  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    const csrfToken = localStorage.getItem('csrfToken');
    if (csrfToken) {
      const cloned = req.clone({
        headers: req.headers.set('X-CSRF-Token', csrfToken)
      });
      return next.handle(cloned);
    } else {
      return next.handle(req);
    }
  }
}
