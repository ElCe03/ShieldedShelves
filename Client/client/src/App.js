import React, { useState } from 'react';
import RegisterForm from './RegisterForm';
import HomePage from './HomePage';
import 'bootstrap/dist/css/bootstrap.min.css'; // Importa Bootstrap CSS

function App() {
  const [showRegisterForm, setShowRegisterForm] = useState(false);

  const handleShowRegisterForm = () => {
    setShowRegisterForm(true);
  };

  return (
    <div className="App">
      {showRegisterForm ? (
        <RegisterForm />
      ) : (
        <HomePage onShowRegisterForm={handleShowRegisterForm} />
      )}
    </div>
  );
}

export default App;
