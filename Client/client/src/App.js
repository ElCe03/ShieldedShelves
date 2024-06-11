import React, { useState } from 'react';
import RegisterForm from './RegisterForm';
import LoginForm from './LoginForm';
import LoginAdmin from './LoginAdmin';
import HomePage from './HomePage';
import LoggedIn from './LoggedIn';
import ListaUtenti from './ListaUtenti'; 
import 'bootstrap/dist/css/bootstrap.min.css';
import { BrowserRouter as Router, Route, Routes, Link, Navigate } from 'react-router-dom';
import { Button, Nav, Navbar, Container } from 'react-bootstrap';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isAdminLoggedIn, setIsAdminLoggedIn] = useState(false); 

  const handleLogin = () => {
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
  };

  const handleAdminLogin = () => { 
    setIsAdminLoggedIn(true);
  };

  const handleAdminLogout = () => { 
    setIsAdminLoggedIn(false);
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
                    {!isAdminLoggedIn && <Nav.Link as={Link} to="/register">Register</Nav.Link>}
                    {!isAdminLoggedIn && <Nav.Link as={Link} to="/login">Login</Nav.Link>}
                  </>
                )}
                {isAdminLoggedIn ? ( 
                  <Nav.Link as={Link} to="/admin/utenti">Lista Utenti</Nav.Link>
                ) : null}
              </Nav>
            </Navbar.Collapse>
          </Container>
        </Navbar>

        <Routes>
          {isAdminLoggedIn ? (
            <Route path="/register" element={<Navigate to="/" />} />
          ) : (
            <Route path="/register" element={<RegisterForm />} />
          )}
          {isAdminLoggedIn ? (
            <Route path="/login" element={<Navigate to="/" />} />
          ) : (
            <Route path="/login" element={<LoginForm onLogin={handleLogin} />} />
          )}
          <Route path="/admin/login" element={<LoginAdmin onLogin={handleAdminLogin} />} />
          <Route path="/logged" element={isLoggedIn ? <LoggedIn /> : <HomePage isAuthenticated={isLoggedIn} />} />
          <Route path="/admin/utenti" element={isAdminLoggedIn ? <ListaUtenti /> : <HomePage isAuthenticated={isLoggedIn} />} /> 
          <Route path="/" element={<HomePage isAuthenticated={isLoggedIn} />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
