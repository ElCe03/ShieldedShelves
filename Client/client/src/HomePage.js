import React from 'react';

const HomePage = ({ onShowRegisterForm }) => {
  return (
    <div>
      <header className="bg-dark text-white py-4">
        <div className="container">
          <div className="row">
            <div className="col">
              <h2 className="text-center">ShieldedShelves</h2>
            </div>
            <div className="col text-right">
              <button onClick={onShowRegisterForm} className="btn btn-primary">Register</button>
            </div>
          </div>
        </div>
      </header>

      <div className="container">
        <div className="row">
          <div className="col-md-8 offset-md-2">
            <img src="/path/to/your/image.jpg" className="img-fluid rounded mb-4" alt="Welcome Image" />
            <h1 className="text-center mb-4">Welcome to ShieldedShelves</h1>
            <p className="text-center">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
          </div>
        </div>
      </div>

      <footer className="bg-secondary text-white py-4 mt-5">
        <div className="container">
          <div className="row">
            <div className="col">
              <p className="text-center">© 2024 ShieldedShelves. All Rights Reserved.</p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;
