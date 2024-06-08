import React from 'react';
import myIcon from './icon.png';
import './HomePage.css'; 

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
              <button onClick={onShowRegisterForm} className="btn btn-primary">Registrati</button>
              <button onClick={onShowRegisterForm} className="btn btn-primary">Login utenti</button>
              <button onClick={onShowRegisterForm} className="btn btn-primary">Login admin</button>
            </div>
          </div>
        </div>
      </header>

      <div className="container">
        <div className="row">
          <div className="col-md-8 offset-md-2 text-center">
            <img src={myIcon} className="rounded mb-4 custom-icon" alt="ShieldedShelves" />
            <h1 className="text-center mb-4">Benvenuti a ShieldedShelves</h1>
            <p className="text-center">Benvenuti in ShieldedShelves, la piattaforma di gestione bibliotecaria che mette al primo posto la sicurezza e la protezione dei vostri preziosi tesori letterari. Con ShieldedShelves, potete dormire sonni tranquilli sapendo che i vostri dati sensibili e i libri più preziosi sono al sicuro da qualsiasi minaccia esterna. Siamo entusiasti di accompagnarvi in questo viaggio verso una gestione bibliotecaria sicura, efficiente e all'avanguardia.</p>
          </div>
        </div>
      </div>

      <footer className="bg-dark text-white py-4 mt-5">
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
