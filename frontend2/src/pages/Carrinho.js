import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Carrinho() {
  const [produtos, setProdutos] = useState([]);
  const [valorTotal, setValorTotal] = useState('0.00');
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  // Carrega os produtos do carrinho
  useEffect(() => {
    fetch('http://localhost:5000/colecao')
      .then(res => res.json())
      .then(data => {
        setProdutos(data.pelucias || []);
        setValorTotal(data.valor_total || '0.00');
        setLoading(false);
      })
      .catch(() => {
        alert('Erro ao carregar carrinho');
        setLoading(false);
      });
  }, []);

  function remover_do_carrinho(e, peluciaId) {
    e.stopPropagation();

    fetch(`http://localhost:5000/colecao/${peluciaId}`, {
      method: 'DELETE'
    })
      .then(res => res.json())
      .then(data => {
        alert(data.mensagem || data.erro);

        if (data.mensagem) {
          const novaLista = [...produtos];
          const index = novaLista.findIndex(p => p.id === peluciaId);
          if (index !== -1) {
            novaLista.splice(index, 1);
            setProdutos(novaLista);

            const novoTotal = novaLista.reduce((total, p) => total + p.preco, 0);
            setValorTotal(novoTotal.toFixed(2));
          }
        }
      })
      .catch(() => alert('Erro ao remover do carrinho'));
  }

  if (loading) return <div>Carregando coleção...</div>;

  return (
    <div className="pagina-inicial">
      <button className="botao-perfil" onClick={() => navigate('/paginaInicial')}>
        Voltar
      </button>
      <h1>Coleção de Pelúcias</h1>

      <div className="lista-produtos">
        {produtos.length === 0 && <p>Sua coleção está vazia.</p>}

        {produtos.map((pelucia) => (
          <div key={pelucia.id} className="card-produto">
            <img src={pelucia.imagem_url} alt={pelucia.nome} className="imagem-produto" />
            <h3>{pelucia.nome}</h3>
            <p>Preço: R$ {pelucia.preco.toFixed(2)}</p>

            <button
              className="botao-carrinho remover"
              onClick={(e) => remover_do_carrinho(e, pelucia.id)}
              aria-label={`Remover ${pelucia.nome} da coleção`}
              title="Remover da coleção"
            >
              <svg
                className="icone-carrinho"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="white"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                width="20"
                height="20"
              >
                <circle cx="9" cy="21" r="1"></circle>
                <circle cx="20" cy="21" r="1"></circle>
                <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
              </svg>
            </button>
          </div>
        ))}
      </div>

      <div className="carrinho-footer">
        <span className="precoTotal">Total: R$ {valorTotal}</span>
        <button className="confirmarCompra">Confirmar compra</button>
      </div>
    </div>
  );
}
