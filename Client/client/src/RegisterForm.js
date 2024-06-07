import React, { useState } from 'react';
import axios from './axiosConfig';
import zxcvbn from 'zxcvbn'; 

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
      const response = await axios.post('/register', formData);
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
    <div>
      <h1>Register</h1>
      <form onSubmit={handleSubmit}>
        <label>
          First Name:
          <input type="text" name="first_name" value={formData.first_name} onChange={handleChange} required />
        </label>
        <br />
        <label>
          Last Name:
          <input type="text" name="last_name" value={formData.last_name} onChange={handleChange} required />
        </label>
        <br />
        <label>
          Email:
          <input type="email" name="email" value={formData.email} onChange={handleChange} required />
        </label>
        <br />
        <label>
          Password:
          <input type="password" name="password" value={formData.password} onChange={handlePasswordChange} required />
          <div>Password Strength: {passwordStrength}</div>
        </label>
        <br />
        <button type="submit">Register</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
};

export default RegisterForm;
