import React, { useState, useEffect } from 'react';
import { axiosInstance5000 } from './axiosConfig';
import zxcvbn from 'zxcvbn';
import { Form, Button, Container, Row, Col, Alert } from 'react-bootstrap';
import xss from 'xss'; 

const RegisterForm = () => {
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    password: ''
  });
  const [message, setMessage] = useState('');
  const [passwordStrength, setPasswordStrength] = useState('');
  const [validationErrors, setValidationErrors] = useState({});

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
    
    const errors = validateForm(formData);
    if (Object.keys(errors).length > 0) {
      setValidationErrors(errors);
      return;
    }

    const sanitizedFormData = {
      first_name: xss(formData.first_name),
      last_name: xss(formData.last_name),
      email: xss(formData.email),
      password: xss(formData.password)
    };

    try {
      const response = await axiosInstance5000.post('/register', sanitizedFormData);
      setMessage(response.data.message);
    } catch (error) {
      if (error.response) {
        setMessage(error.response.data.message || 'Registration failed');
      } else {
        setMessage('Error: Could not connect to the server');
      }
    }
  };

  const validateForm = (data) => {
    let errors = {};

    if (!data.first_name.trim()) {
      errors.first_name = 'First name is required';
    }

    if (!data.last_name.trim()) {
      errors.last_name = 'Last name is required';
    }

    if (!data.email.trim()) {
      errors.email = 'Email is required';
    } else if (!isValidEmail(data.email)) {
      errors.email = 'Invalid email format';
    }

    if (!data.password.trim()) {
      errors.password = 'Password is required';
    } else if (data.password.length < 8) {
      errors.password = 'Password must be at least 8 characters long';
    }

    return errors;
  };

  const isValidEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
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
              {validationErrors.first_name && <span className="text-danger">{validationErrors.first_name}</span>}
            </Form.Group>
            <Form.Group controlId="formLastName">
              <Form.Label>Last Name:</Form.Label>
              <Form.Control type="text" name="last_name" value={formData.last_name} onChange={handleChange} required />
              {validationErrors.last_name && <span className="text-danger">{validationErrors.last_name}</span>}
            </Form.Group>
            <Form.Group controlId="formEmail">
              <Form.Label>Email:</Form.Label>
              <Form.Control type="email" name="email" value={formData.email} onChange={handleChange} required />
              {validationErrors.email && <span className="text-danger">{validationErrors.email}</span>}
            </Form.Group>
            <Form.Group controlId="formPassword">
              <Form.Label>Password:</Form.Label>
              <Form.Control type="password" name="password" value={formData.password} onChange={handlePasswordChange} required />
              <Form.Text>Password Strength: {passwordStrength}</Form.Text>
              {validationErrors.password && <span className="text-danger">{validationErrors.password}</span>}
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
