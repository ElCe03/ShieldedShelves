import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';


@Component({
  selector: 'app-register',
  templateUrl: './register.component.html'
})
export class RegisterComponent {
  registerForm: FormGroup;

  constructor(private fb: FormBuilder, private http: HttpClient, ) {
    this.registerForm = this.fb.group({
      first_name: ['', Validators.required],
      last_name: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required]
    });
  }

  onSubmit() {
    if (this.registerForm.valid) {
      this.http.post('http://localhost:5000/register', this.registerForm.value).subscribe(response => {
        console.log('User registered successfully');
      }, error => {
        console.error('Error registering user', error);
      });
    }
  }

  sanitizeInput(controlName: string) {
    const control = this.registerForm.get(controlName);
    if (control && control.value) {
      control.setValue(control.value.replace(/<[^>]*>?/gm, ''));
    }
  }
}
