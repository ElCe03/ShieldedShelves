import React, { useState, useEffect } from 'react';
import { axiosInstance5001 } from './axiosConfig';
import { Form, Button, Container, Row, Col, Alert } from 'react-bootstrap';
import xss from 'xss'; 

const LoginForm = ({ onLogin }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [message, setMessage] = useState('');

  useEffect(() => {
    const fetchCsrfToken = async () => {
      try {
        const response = await axiosInstance5001.get('/get_csrf_token');
        axiosInstance5001.defaults.headers.post['X-CSRF-Token'] = response.data.csrf_token;
      } catch (error) {
        console.error('Error fetching CSRF token:', error);
      }
    };

    fetchCsrfToken();
  }, []);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const validateInput = () => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      setMessage('Invalid email address');
      return false;
    }

    if (formData.password.length < 8) {
      setMessage('Password must be at least 8 characters long');
      return false;
    }

    setMessage('');
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateInput()) {
      return;
    }

    const sanitizedFormData = {
      email: xss(formData.email),
      password: xss(formData.password)
    };

    try {
      const response = await axiosInstance5001.post('/login', sanitizedFormData);
      setMessage(response.data.message);
      if (response.status === 200) {
        onLogin();
      }
    } catch (error) {
      if (error.response) {
        setMessage(error.response.data.message || 'Login failed');
      } else {
        setMessage('Error: Could not connect to the server');
      }
    }
  };

  return (
    <Container>
      <Row className="justify-content-md-center">
        <Col md={6}>
          <h1 className="text-center mb-4">Login</h1>
          <Form onSubmit={handleSubmit}>
            <Form.Group controlId="formEmail">
              <Form.Label>Email:</Form.Label>
              <Form.Control type="email" name="email" value={formData.email} onChange={handleChange} required />
            </Form.Group>
            <Form.Group controlId="formPassword">
              <Form.Label>Password:</Form.Label>
              <Form.Control type="password" name="password" value={formData.password} onChange={handleChange} required />
            </Form.Group>
            <Button variant="primary" type="submit" block>Login</Button>
          </Form>
          {message && <Alert className="mt-3" variant={message.includes('success') ? 'success' : 'danger'}>{message}</Alert>}
        </Col>
      </Row>
    </Container>
  );
};

export default LoginForm;
