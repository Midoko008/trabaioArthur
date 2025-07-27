import React, { useState } from 'react';
import '../App.css';

export default function Cadastro() {
  const [form, setForm] = useState({
    nome: '',
    email: '',
    cep: '',
    cpf: '',
    data_nascimento: '',
    senha: '',
  });

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Aqui você faz o fetch para seu backend
    fetch('http://localhost:5000/cadastro', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form),
    })
      .then(res => res.json())
      .then(data => alert(data.mensagem || data.erro))
      .catch(() => alert('Erro ao cadastrar.'));
  };

  return (
    <div className="container">
      <h2>Cadastro de Usuário</h2>
      <form onSubmit={handleSubmit} className="formulario">
        {['nome', 'email', 'cep', 'cpf', 'data_nascimento', 'senha'].map((campo) => (
          <input
            key={campo}
            type={campo === 'senha' ? 'password' : campo === 'data_nascimento' ? 'date' : 'text'}
            name={campo}
            placeholder={campo.replace('_', ' ').toUpperCase()}
            value={form[campo]}
            onChange={handleChange}
            required
          />
        ))}
        <button type="submit">Cadastrar</button>
      </form>
    </div>
  );
}
