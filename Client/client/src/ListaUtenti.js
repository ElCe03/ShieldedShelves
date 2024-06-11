import React, { useState, useEffect } from 'react';
import { axiosInstance5003 } from './axiosConfig';
import { Container, Table, Button, Modal, Form } from 'react-bootstrap';

function ListaUtenti() {
  const [users, setUsers] = useState([]);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({ id: '', first_name: '', last_name: '', email: '' });

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await axiosInstance5003.get('/users');
      setUsers(response.data);
    } catch (error) {
      setError('Errore nel recupero degli utenti');
    }
  };

  const handleDelete = async (userId) => {
    try {
      await axiosInstance5003.delete(`/users/${userId}`);
      fetchUsers();
    } catch (error) {
      setError('Errore nella cancellazione dell\'utente');
    }
  };

  const handleEdit = (user) => {
    setFormData(user);
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setFormData({ id: '', first_name: '', last_name: '', email: '' });
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axiosInstance5003.put(`/users/${formData.id}`, formData);
      fetchUsers();
      handleCloseModal();
    } catch (error) {
      setError('Errore nell\'aggiornamento dell\'utente');
    }
  };

  return (
    <Container>
      <h2>Lista Utenti</h2>
      {error && <p>{error}</p>}
      <Table striped bordered hover>
        <thead>
          <tr>
            <th>ID</th>
            <th>Nome</th>
            <th>Cognome</th>
            <th>Email</th>
            <th>Azioni</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user) => (
            <tr key={user.id}>
              <td>{user.id}</td>
              <td>{user.first_name}</td>
              <td>{user.last_name}</td>
              <td>{user.email}</td>
              <td>
                <Button variant="primary" onClick={() => handleEdit(user)}>Modifica</Button>{' '}
                <Button variant="danger" onClick={() => handleDelete(user.id)}>Elimina</Button>
              </td>
            </tr>
          ))}
        </tbody>
      </Table>

      <Modal show={showModal} onHide={handleCloseModal}>
        <Modal.Header closeButton>
          <Modal.Title>Modifica Utente</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form onSubmit={handleSubmit}>
            <Form.Group controlId="formBasicFirstName">
              <Form.Label>Nome</Form.Label>
              <Form.Control type="text" placeholder="Inserisci il nome" name="first_name" value={formData.first_name} onChange={handleChange} required />
            </Form.Group>
            <Form.Group controlId="formBasicLastName">
              <Form.Label>Cognome</Form.Label>
              <Form.Control type="text" placeholder="Inserisci il cognome" name="last_name" value={formData.last_name} onChange={handleChange} required />
            </Form.Group>
            <Form.Group controlId="formBasicEmail">
              <Form.Label>Email</Form.Label>
              <Form.Control type="email" placeholder="Inserisci l'email" name="email" value={formData.email} onChange={handleChange} required />
            </Form.Group>
            <Button variant="primary" type="submit">
              Salva Modifiche
            </Button>
          </Form>
        </Modal.Body>
      </Modal>
    </Container>
  );
}

export default ListaUtenti;