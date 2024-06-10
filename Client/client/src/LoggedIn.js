import React from 'react';
import { Container, Row, Col } from 'react-bootstrap';

const LoggedIn = () => (
  <Container>
    <Row className="justify-content-md-center text-center">
      <Col md={8}>
        <h1 className="mb-4">Protected Page</h1>
        <p>This page is only accessible to authenticated users.</p>
      </Col>
    </Row>
  </Container>
);

export default LoggedIn;