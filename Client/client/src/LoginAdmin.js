import React, { useState } from 'react';
import { axiosInstance5002 } from './axiosConfig';
import { useNavigate } from 'react-router-dom';
import xss from 'xss'; 

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
      const sanitizedFormData = {
        email: xss(formData.email),
        password: xss(formData.password)
      };
      const response = await axiosInstance5002.post('/login', sanitizedFormData);
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
      const sanitizedFormData = {
        email: xss(formData.email),
        otp: xss(otp)
      };
      const response = await axiosInstance5002.post('/verify_otp', sanitizedFormData);
      if (response.data.message === 'Login successful') {
        onLogin();
        navigate('/admin');
      }
    } catch (error) {
      setError('Invalid OTP or user not found');
    }
  };

  return (
    <div className="container">
      <div className="row justify-content-center">
        <div className="col-md-6">
          <div className="card">
            <div className="card-body">
              {step === 1 ? (
                <form onSubmit={handleSubmit}>
                  <div className="mb-3">
                    <label htmlFor="email" className="form-label">Email:</label>
                    <input type="email" id="email" className="form-control" name="email" value={formData.email} onChange={handleChange} required />
                  </div>
                  <div className="mb-3">
                    <label htmlFor="password" className="form-label">Password:</label>
                    <input type="password" id="password" className="form-control" name="password" value={formData.password} onChange={handleChange} required />
                  </div>
                  <button type="submit" className="btn btn-primary">Login</button>
                </form>
              ) : (
                <form onSubmit={handleOtpSubmit}>
                  <div className="mb-3">
                    <label htmlFor="otp" className="form-label">OTP:</label>
                    <input type="text" id="otp" className="form-control" value={otp} onChange={handleOtpChange} required />
                  </div>
                  <button type="submit" className="btn btn-primary">Verify OTP</button>
                </form>
              )}
              {error && <p className="text-danger">{error}</p>}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LoginAdmin;
