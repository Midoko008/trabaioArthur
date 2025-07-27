import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import '../App.css';

export default function Login() {
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    fetch('http://localhost:5000/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, senha }),
    })
      .then(res => res.json())
      .then(data => {
        alert(data.mensagem || data.erro);
        if (data.usuario) {
          // Salva usuário no localStorage como string JSON
          localStorage.setItem('usuario', JSON.stringify(data.usuario));
          navigate('/paginaInicial');
        }
      })
      .catch(() => alert('Erro ao fazer login.'));
  };

  return (
    <div className="container">
      <h2>Login</h2>
      <form onSubmit={handleSubmit} className="formulario">
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={e => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Senha"
          value={senha}
          onChange={e => setSenha(e.target.value)}
          required
        />
        <button type="submit">Entrar</button>
      </form>

      <p style={{ textAlign: 'center' }}>
        Não tem conta?{' '}
        <Link to="/cadastro" style={{ color: '#007bff', textDecoration: 'none' }}>
          Cadastre-se
        </Link>
      </p>
    </div>
  );
}
