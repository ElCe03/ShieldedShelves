import React, { useState } from 'react';
import { axiosInstance5000 } from './axiosConfig';import zxcvbn from 'zxcvbn'; 
import 'bootstrap/dist/css/bootstrap.min.css';

const RegisterForm = () => {
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    password: ''
  });
  const [message, setMessage] = useState('');
  const [passwordStrength, setPasswordStrength] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handlePasswordChange = (e) => {
    setFormData({
      ...formData,
      password: e.target.value
    });

    calculatePasswordStrength(e.target.value);
  };

  const calculatePasswordStrength = (password) => {
    const strength = zxcvbn(password);

    switch (strength.score) {
      case 0:
        setPasswordStrength('Very Weak');
        break;
      case 1:
        setPasswordStrength('Weak');
        break;
      case 2:
        setPasswordStrength('Fair');
        break;
      case 3:
        setPasswordStrength('Strong');
        break;
      case 4:
        setPasswordStrength('Very Strong');
        break;
      default:
        setPasswordStrength('');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axiosInstance5000.post('/register', formData);
      setMessage(response.data.message);
    } catch (error) {
      if (error.response) {
        setMessage(error.response.data.message || 'Registration failed');
      } else {
        setMessage('Error: Could not connect to the server');
      }
    }
  };

  return (
    <div className="container">
      <div className="row">
        <div className="col-md-6 offset-md-3">
          <h1 className="text-center mb-4">Register</h1>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>First Name:</label>
              <input type="text" name="first_name" value={formData.first_name} onChange={handleChange} className="form-control" required />
            </div>
            <div className="form-group">
              <label>Last Name:</label>
              <input type="text" name="last_name" value={formData.last_name} onChange={handleChange} className="form-control" required />
            </div>
            <div className="form-group">
              <label>Email:</label>
              <input type="email" name="email" value={formData.email} onChange={handleChange} className="form-control" required />
            </div>
            <div className="form-group">
              <label>Password:</label>
              <input type="password" name="password" value={formData.password} onChange={handlePasswordChange} className="form-control" required />
              <div>Password Strength: {passwordStrength}</div>
            </div>
            <button type="submit" className="btn btn-primary btn-block">Register</button>
          </form>
          {message && <p className="mt-3 text-center">{message}</p>}
        </div>
      </div>
    </div>
  );
};

export default RegisterForm;
