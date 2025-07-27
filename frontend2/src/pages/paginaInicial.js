import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../App.css';

export default function PaginaInicial() {
  const [produtosFiltrados, setProdutosFiltrados] = useState([]);
  const [filtro, setFiltro] = useState('');
  const [categorias, setCategorias] = useState([]);
  const [categoriaSelecionada, setCategoriaSelecionada] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetch('http://localhost:5000/categorias')
      .then(res => res.json())
      .then(data => setCategorias(data))
      .catch(err => console.error('Erro ao buscar categorias:', err));
  }, []);

  useEffect(() => {
    let url = 'http://localhost:5000/pelucias';

    const termo = filtro.trim();
    if (termo) {
      url = `http://localhost:5000/pelucias/buscar?q=${encodeURIComponent(termo)}`;
    } else if (categoriaSelecionada) {
      url = `http://localhost:5000/pelucias/categoria/${categoriaSelecionada}`;
    }

    fetch(url)
      .then(res => res.json())
      .then(data => setProdutosFiltrados(data))
      .catch(err => {
        console.error('Erro ao buscar produtos:', err);
        setProdutosFiltrados([]);
      });
  }, [filtro, categoriaSelecionada]);

  function irParaPerfil() {
    navigate('/perfil');
  }

  function abrirDetalhes(id) {
    navigate(`/pelucia/${id}`);
  }

  function irParaAdicionarProduto() {
    navigate('/adicionar-produto');
  }

  function irParaCarrinho() {
    navigate('/colecao');
  }

  function adicionarAoCarrinho(e, produtoId) {
    e.stopPropagation();
    fetch('http://localhost:5000/colecao', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pelucia_id: produtoId }),
    })
      .then(res => res.json())
      .then(data => alert(data.mensagem || data.erro))
      .catch(() => alert('Erro ao adicionar à coleção'));
  }

  return (
    <div className="pagina-inicial">
      <header className="header">
        <h1>Feed de Pelúcias</h1>
        <div className="botoes-topo">
          <button className="botao-perfil" onClick={irParaPerfil}>Ver Perfil</button>
          <button className="botao-adicionar" onClick={irParaAdicionarProduto}>Adicionar Pelúcia</button>
          <button
            className="botao-carrinho topo"
            onClick={irParaCarrinho}
            aria-label="Ver carrinho"
            title="Ver coleção"
          >
<svg
  xmlns="http://www.w3.org/2000/svg"
  viewBox="0 0 24 24"
  width="24"
  height="24"
  fill="none"
  stroke="currentColor"
  strokeWidth="1.5"
  strokeLinecap="round"
  strokeLinejoin="round"
>
  {/* Metade superior */}
  <path d="M2 12h20a10 10 0 0 0-20 0z" fill="#f44336" stroke="black" />
  {/* Metade inferior */}
  <path d="M2 12h20a10 10 0 0 1-20 0z" fill="white" stroke="black" />
  {/* Linha divisória */}
  <line x1="2" y1="12" x2="22" y2="12" stroke="black" />
  {/* Círculo central externo */}
  <circle cx="12" cy="12" r="3" fill="white" stroke="black" />
  {/* Círculo central interno */}
  <circle cx="12" cy="12" r="1" fill="black" />
</svg>

          </button>
        </div>
      </header>

      {/* Barra de busca com classe */}
      <div className="filtros-container">
      <input
        type="text"
        placeholder="Buscar pelucias pelo nome..."
        value={filtro}
        onChange={e => {
          setFiltro(e.target.value);
          setCategoriaSelecionada('');
        }}
        className="barra-pesquisa"
      />

      {/* Filtro de categoria com classe */}
      <select
        value={categoriaSelecionada}
        onChange={e => {
          setCategoriaSelecionada(e.target.value);
          setFiltro('');
        }}
        className="select-categoria"
      >
        <option value="">Filtrar por categoria...</option>
        {categorias.map(c => (
          <option key={c.id} value={c.id}>{c.nome}</option>
        ))}
      </select>
      </div>

      <div className="lista-produtos">
        {produtosFiltrados.length === 0 ? (
          <p>Nenhuma pelúcia encontrado.</p>
        ) : (
          produtosFiltrados.map(produto => (
            <div
              key={produto.id}
              className="card-produto"
              onClick={() => abrirDetalhes(produto.id)}
            >
              <img
                src={produto.imagem_url}
                alt={produto.nome}
                className="imagem-produto"
                onError={(e) => {
                  e.target.onerror = null;
                  e.target.src = '/img/imagem-nao-disponivel.png';
                }}
              />
              <h3>{produto.nome}</h3>
              <p>Preço: R$ {produto.preco.toFixed(2)}</p>
              <button
                className="botao-carrinho card"
                onClick={(e) => adicionarAoCarrinho(e, produto.id)}
                aria-label={`Adicionar ${produto.nome} à coleção`}
                title="Adicionar à coleção"
              >
<svg
  xmlns="http://www.w3.org/2000/svg"
  viewBox="0 0 24 24"
  width="24"
  height="24"
  fill="none"
  stroke="currentColor"
  strokeWidth="1.5"
  strokeLinecap="round"
  strokeLinejoin="round"
>
  {/* Metade superior */}
  <path d="M2 12h20a10 10 0 0 0-20 0z" fill="#f44336" stroke="black" />
  {/* Metade inferior */}
  <path d="M2 12h20a10 10 0 0 1-20 0z" fill="white" stroke="black" />
  {/* Linha divisória */}
  <line x1="2" y1="12" x2="22" y2="12" stroke="black" />
  {/* Círculo central externo */}
  <circle cx="12" cy="12" r="3" fill="white" stroke="black" />
  {/* Círculo central interno */}
  <circle cx="12" cy="12" r="1" fill="black" />
</svg>


              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
