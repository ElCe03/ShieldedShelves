import React, { useState } from 'react';
import RegisterForm from './RegisterForm';
import LoginForm from './LoginForm';
import LoginAdmin from './LoginAdmin';
import HomePage from './HomePage';
import LoggedIn from './LoggedIn'; 
import 'bootstrap/dist/css/bootstrap.min.css';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import { Button, Nav, Navbar, Container } from 'react-bootstrap';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const handleLogin = () => {
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
  };

  return (
    <Router>
      <div className="App">
        <Navbar bg="dark" variant="dark" expand="lg">
          <Container>
            <Navbar.Brand as={Link} to="/">ShieldedShelves</Navbar.Brand>
            <Navbar.Toggle aria-controls="basic-navbar-nav" />
            <Navbar.Collapse id="basic-navbar-nav">
              <Nav className="ml-auto">
                {isLoggedIn ? (
                  <>
                    <Nav.Link as={Link} to="/logged">LoggedIn</Nav.Link>
                    <Button onClick={handleLogout} className="nav-link btn btn-link">Logout</Button>
                  </>
                ) : (
                  <>
                    <Nav.Link as={Link} to="/register">Register</Nav.Link>
                    <Nav.Link as={Link} to="/login">Login</Nav.Link>
                  </>
                )}
              </Nav>
            </Navbar.Collapse>
          </Container>
        </Navbar>

        <Routes>
          <Route path="/register" element={<RegisterForm />} />
          <Route path="/login" element={<LoginForm onLogin={handleLogin} />} />
          <Route path="/admin/login" element={<LoginAdmin onLogin={handleLogin} />} />
          <Route path="/logged" element={isLoggedIn ? <LoggedIn /> : <HomePage isAuthenticated={isLoggedIn} />} />
          <Route path="/" element={<HomePage isAuthenticated={isLoggedIn} />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
