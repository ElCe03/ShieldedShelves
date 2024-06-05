import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.css'] // Make sure you have a CSS file to style the error messages
})
export class RegisterComponent {
  registerForm: FormGroup;
  passwordStrengthMessage: string | null = null;

  constructor(private fb: FormBuilder, private http: HttpClient) {
    this.registerForm = this.fb.group({
      first_name: ['', Validators.required],
      last_name: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required]
    });
  }

  onSubmit() {
    this.passwordStrengthMessage = this.checkPasswordStrength(this.registerForm.get('password')?.value);
    if (this.registerForm.valid && !this.passwordStrengthMessage) {
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

  checkPasswordStrength(password: string): string | null {
    if (!password) return 'Password is required';
    const minLength = 8;
    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasNumbers = /\d/.test(password);
    const hasSpecialChars = /[!@#$%^&*(),.?":{}|<>]/.test(password);

    if (password.length < minLength) {
      return `Password must be at least ${minLength} characters long`;
    }
    if (!hasUpperCase) {
      return 'Password must contain at least one uppercase letter';
    }
    if (!hasLowerCase) {
      return 'Password must contain at least one lowercase letter';
    }
    if (!hasNumbers) {
      return 'Password must contain at least one number';
    }
    if (!hasSpecialChars) {
      return 'Password must contain at least one special character';
    }
    return null;
  }
}
