import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent, HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';

@Injectable()
export class CsrfInterceptor implements HttpInterceptor {
  constructor(private http: HttpClient) {}

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    return this.http.get<any>('http://localhost:5000/get_csrf_token').pipe(
      tap((data: any) => { 
        const csrfReq = req.clone({
          headers: req.headers.set('X-CSRF-Token', data.csrf_token)
        });
        return next.handle(csrfReq);
      })
    );
  }
}
