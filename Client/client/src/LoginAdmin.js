import React, { useState } from 'react';
import { axiosInstance5002 } from './axiosConfig';
import { useNavigate } from 'react-router-dom';

function LoginAdmin({ onLogin }) {
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [otp, setOtp] = useState('');
  const [step, setStep] = useState(1);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleOtpChange = (e) => {
    setOtp(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axiosInstance5002.post('/login', formData);
      if (response.data.message === 'OTP sent to your phone number') {
        setStep(2);
      }
    } catch (error) {
      setError('Invalid credentials or user not found');
    }
  };

  const handleOtpSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axiosInstance5002.post('/verify_otp', { email: formData.email, otp });
      if (response.data.message === 'Login successful') {
        onLogin();
        navigate('/admin');
      }
    } catch (error) {
      setError('Invalid OTP or user not found');
    }
  };

  return (
    <div>
      {step === 1 ? (
        <form onSubmit={handleSubmit}>
          <div>
            <label>Email:</label>
            <input type="email" name="email" value={formData.email} onChange={handleChange} required />
          </div>
          <div>
            <label>Password:</label>
            <input type="password" name="password" value={formData.password} onChange={handleChange} required />
          </div>
          <button type="submit">Login</button>
        </form>
      ) : (
        <form onSubmit={handleOtpSubmit}>
          <div>
            <label>OTP:</label>
            <input type="text" value={otp} onChange={handleOtpChange} required />
          </div>
          <button type="submit">Verify OTP</button>
        </form>
      )}
      {error && <p>{error}</p>}
    </div>
  );
}

export default LoginAdmin;
