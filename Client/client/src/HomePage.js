import React from 'react';
import { Container, Row, Col, Image } from 'react-bootstrap';
import myIcon from './icon.png';
import './HomePage.css';

const HomePage = ({ isAuthenticated }) => (
  <div>
    <Container>
      <Row className="justify-content-md-center text-center">
        <Col md={8}>
          <Image src={myIcon} rounded className="mb-4 custom-icon" alt="ShieldedShelves" />
          <h1 className="mb-4">Benvenuti a ShieldedShelves</h1>
          <p>
            Benvenuti in ShieldedShelves, la piattaforma di gestione bibliotecaria che mette al primo posto la sicurezza e la protezione dei vostri preziosi tesori letterari. Con ShieldedShelves, potete dormire sonni tranquilli sapendo che i vostri dati sensibili e i libri più preziosi sono al sicuro da qualsiasi minaccia esterna. Siamo entusiasti di accompagnarvi in questo viaggio verso una gestione bibliotecaria sicura, efficiente e all'avanguardia.
          </p>
        </Col>
      </Row>
    </Container>

    <footer className="bg-dark text-white py-4 mt-5">
      <Container>
        <Row>
          <Col className="text-center">
            <p>© 2024 ShieldedShelves. All Rights Reserved.</p>
          </Col>
        </Row>
      </Container>
    </footer>
  </div>
);

export default HomePage;
