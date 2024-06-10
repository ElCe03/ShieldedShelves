import React, { useState, useEffect } from 'react';
import { axiosInstance5000 } from './axiosConfig';
import zxcvbn from 'zxcvbn';
import { Form, Button, Container, Row, Col, Alert } from 'react-bootstrap';

const RegisterForm = () => {
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    password: ''
  });
  const [message, setMessage] = useState('');
  const [passwordStrength, setPasswordStrength] = useState('');

  useEffect(() => {
    const fetchCsrfToken = async () => {
      try {
        const response = await axiosInstance5000.get('/get_csrf_token');
        axiosInstance5000.defaults.headers.post['X-CSRF-Token'] = response.data.csrf_token;
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
    <Container>
      <Row className="justify-content-md-center">
        <Col md={6}>
          <h1 className="text-center mb-4">Register</h1>
          <Form onSubmit={handleSubmit}>
            <Form.Group controlId="formFirstName">
              <Form.Label>First Name:</Form.Label>
              <Form.Control type="text" name="first_name" value={formData.first_name} onChange={handleChange} required />
            </Form.Group>
            <Form.Group controlId="formLastName">
              <Form.Label>Last Name:</Form.Label>
              <Form.Control type="text" name="last_name" value={formData.last_name} onChange={handleChange} required />
            </Form.Group>
            <Form.Group controlId="formEmail">
              <Form.Label>Email:</Form.Label>
              <Form.Control type="email" name="email" value={formData.email} onChange={handleChange} required />
            </Form.Group>
            <Form.Group controlId="formPassword">
              <Form.Label>Password:</Form.Label>
              <Form.Control type="password" name="password" value={formData.password} onChange={handlePasswordChange} required />
              <Form.Text>Password Strength: {passwordStrength}</Form.Text>
            </Form.Group>
            <Button variant="primary" type="submit" block>Register</Button>
          </Form>
          {message && <Alert className="mt-3" variant={message.includes('success') ? 'success' : 'danger'}>{message}</Alert>}
        </Col>
      </Row>
    </Container>
  );
};

export default RegisterForm;
