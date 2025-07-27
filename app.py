from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, Usuario, Pelucia, Colecao, Categoria
from datetime import datetime
import bcrypt

app = Flask(__name__)
CORS(app)

# Configuração do banco de dados MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://LimaThur:LigaDasLendas234!@localhost/PeluciasThur'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Função para obter o usuário logado a partir do header Authorization (Bearer <user_id>)
def get_usuario_logado():
    auth = request.headers.get('Authorization')
    if not auth:
        return None
    try:
        token_type, user_id = auth.split()
        if token_type.lower() != 'bearer':
            return None
        user_id_int = int(user_id)
        return Usuario.query.get(user_id_int)
    except Exception:
        return None

# --- Rotas Usuário ---

@app.route('/cadastro', methods=['POST'])
def cadastrar_usuario():
    dados = request.json
    try:
        nascimento = datetime.strptime(dados['data_nascimento'], '%Y-%m-%d').date()
    except (ValueError, KeyError):
        return jsonify({'erro': 'Data de nascimento inválida ou não informada'}), 400

    idade = Usuario.calcular_idade(nascimento)
    senha = dados.get('senha', '')
    if not senha:
        return jsonify({'erro': 'Senha não informada'}), 400

    senha_bytes = senha.encode('utf-8')
    senha_criptografada = bcrypt.hashpw(senha_bytes, bcrypt.gensalt())

    novo_usuario = Usuario(
        nome=dados.get('nome'),
        email=dados.get('email'),
        cep=dados.get('cep'),
        cpf=dados.get('cpf'),
        data_nascimento=nascimento,
        idade=idade,
        senha_hash=senha_criptografada.decode('utf-8'),
        tipo='comum'
    )

    try:
        db.session.add(novo_usuario)
        db.session.commit()
        return jsonify({'mensagem': 'Usuário cadastrado com sucesso!'}), 201
    except Exception:
        db.session.rollback()
        return jsonify({'erro': 'Erro ao cadastrar usuário'}), 500

@app.route('/login', methods=['POST'])
def login():
    dados = request.json
    usuario = Usuario.query.filter_by(email=dados.get('email')).first()

    if usuario and bcrypt.checkpw(dados.get('senha', '').encode(), usuario.senha_hash.encode()):
        return jsonify({
            'mensagem': 'Login bem-sucedido',
            'usuario': {
                'id': usuario.id,
                'nome': usuario.nome,
                'email': usuario.email,
                'cep': usuario.cep,
                'cpf': usuario.cpf,
                'data_nascimento': usuario.data_nascimento.strftime('%Y-%m-%d'),
                'idade': usuario.idade,
                'tipo': usuario.tipo
            }
        }), 200

    return jsonify({'erro': 'E-mail ou senha inválidos'}), 401

@app.route('/usuarios/<int:id>', methods=['GET'])
def obter_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    usuario_logado = get_usuario_logado()
    if not usuario_logado:
        return jsonify({'erro': 'Usuário não autenticado'}), 401

    if usuario_logado.id == usuario.id or usuario_logado.tipo == 'admin':
        return jsonify(usuario.to_dict_completo())
    else:
        return jsonify(usuario.to_dict_publico())

@app.route('/usuarios/me', methods=['GET'])
def obter_meu_perfil():
    usuario_logado = get_usuario_logado()
    if not usuario_logado:
        return jsonify({'erro': 'Usuário não autenticado'}), 401
    return jsonify(usuario_logado.to_dict_completo())

@app.route('/usuarios/<int:id>', methods=['PUT'])
def atualizar_usuario(id):
    usuario_logado = get_usuario_logado()
    if not usuario_logado:
        return jsonify({'erro': 'Usuário não autenticado'}), 401
    if usuario_logado.id != id and usuario_logado.tipo != 'admin':
        return jsonify({'erro': 'Acesso negado'}), 403

    dados = request.json
    usuario = Usuario.query.get_or_404(id)
    if 'nome' in dados:
        usuario.nome = dados['nome']
    if 'email' in dados:
        usuario.email = dados['email']

    try:
        db.session.commit()
        return jsonify({'mensagem': 'Dados atualizados com sucesso'})
    except Exception:
        db.session.rollback()
        return jsonify({'erro': 'Erro ao atualizar usuário'}), 500

# --- Rotas Categoria ---

@app.route('/categorias', methods=['GET'])
def listar_categorias():
    categorias = Categoria.query.all()
    return jsonify([{'id': c.id, 'nome': c.nome} for c in categorias])

@app.route('/categorias', methods=['POST'])
def criar_categoria():
    dados = request.json
    nome = dados.get('nome')
    if not nome:
        return jsonify({'erro': 'Nome da categoria é obrigatório'}), 400

    existente = Categoria.query.filter_by(nome=nome).first()
    if existente:
        return jsonify({'erro': 'Categoria já existe'}), 400

    nova_categoria = Categoria(nome=nome)
    try:
        db.session.add(nova_categoria)
        db.session.commit()
        return jsonify({'mensagem': 'Categoria criada', 'id': nova_categoria.id}), 201
    except Exception:
        db.session.rollback()
        return jsonify({'erro': 'Erro ao criar categoria'}), 500

# --- Rotas pelucia ---

@app.route('/pelucias', methods=['GET'])
def listar_pelucias():
    pelucias = Pelucia.query.all()
    lista = []
    for p in pelucias:
        lista.append({
            'id': p.id,
            'nome': p.nome,
            'preco': p.preco,
            'imagem_url': p.imagem_url,
            'estoque': p.estoque,
            'categoria': {
                'id': p.categoria.id if p.categoria else None,
                'nome': p.categoria.nome if p.categoria else None
            }
        })
    return jsonify(lista)

@app.route('/pelucias/<int:id>', methods=['GET'])
def obter_pelucia(id):
    p = Pelucia.query.get(id)
    if not p:
        return jsonify({'erro': 'pelucia não encontrado'}), 404
    return jsonify({
        'id': p.id,
        'nome': p.nome,
        'preco': p.preco,
        'imagem_url': p.imagem_url,
        'estoque': p.estoque,
        'categoria': {
            'id': p.categoria.id if p.categoria else None,
            'nome': p.categoria.nome if p.categoria else None
        },
        'usuario': {
            'id': p.usuario.id,
            'nome': p.usuario.nome
        }
    })

@app.route('/pelucias', methods=['POST'])
def criar_pelucia():
    usuario_logado = get_usuario_logado()
    if not usuario_logado:
        return jsonify({'erro': 'Usuário não autenticado'}), 401

    dados = request.json
    nome = dados.get('nome')
    preco = dados.get('preco')
    imagem_url = dados.get('imagem_url')
    estoque = dados.get('estoque')
    categoria_id = dados.get('categoria_id')

    if not nome or preco is None or not imagem_url or estoque is None or not categoria_id:
        return jsonify({'erro': 'Dados incompletos'}), 400

    try:
        preco = float(preco)
        estoque = int(estoque)
        categoria_id = int(categoria_id)
        if estoque <= 0:
            return jsonify({'erro': 'Estoque deve ser maior que zero'}), 400
    except (ValueError, TypeError):
        return jsonify({'erro': 'Preço, estoque ou categoria inválidos'}), 400

    categoria = Categoria.query.get(categoria_id)
    if not categoria:
        return jsonify({'erro': 'Categoria não encontrada'}), 404

    novo_pelucia = Pelucia(
        nome=nome,
        preco=preco,
        imagem_url=imagem_url,
        estoque=estoque,
        categoria_id=categoria_id,
        usuario_id=usuario_logado.id
    )

    try:
        db.session.add(novo_pelucia)
        db.session.commit()
        return jsonify({'mensagem': 'pelucia criado com sucesso!'}), 201
    except Exception:
        db.session.rollback()
        return jsonify({'erro': 'Erro ao salvar pelucia'}), 500

@app.route('/pelucias/<int:id>', methods=['DELETE'])
def deletar_pelucia(id):
    usuario_logado = get_usuario_logado()
    if not usuario_logado:
        return jsonify({'erro': 'Usuário não autenticado'}), 401

    pelucia = Pelucia.query.get(id)
    if not pelucia:
        return jsonify({'erro': 'pelucia não encontrado'}), 404

    if usuario_logado.id != pelucia.usuario_id and usuario_logado.tipo != 'admin':
        return jsonify({'erro': 'Acesso negado'}), 403

    try:
        Colecao.query.filter_by(pelucia_id=id).delete()
        db.session.delete(pelucia)
        db.session.commit()
        return jsonify({'mensagem': 'pelucia deletado com sucesso'}), 200
    except Exception:
        db.session.rollback()
        return jsonify({'erro': 'Erro ao deletar pelucia'}), 500

# --- colecao (sem usuário_id) ---

@app.route('/colecao', methods=['POST'])
def adicionar_ao_colecao():
    dados = request.json
    pelucia_id = dados.get('pelucia_id')
    pelucia = Pelucia.query.get(pelucia_id)
    if not pelucia:
        return jsonify({'erro': 'pelucia não encontrado'}), 404
    if pelucia.estoque <= 0:
        return jsonify({'erro': 'pelucia sem estoque'}), 400

    try:
        novo_item = Colecao(pelucia_id=pelucia.id)
        pelucia.estoque -= 1
        db.session.add(novo_item)
        db.session.commit()
        return jsonify({'mensagem': 'pelucia adicionado ao colecao!'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': 'Erro ao adicionar ao colecao', 'detalhe': str(e)}), 500


@app.route('/colecao', methods=['GET'])
def listar_colecao():
    itens = Colecao.query.all()
    pelucias = []
    valor_total = 0.0

    for item in itens:
        p = Pelucia.query.get(item.pelucia_id)
        if p:
            valor_total += p.preco
            pelucias.append({
                'id': p.id,
                'nome': p.nome,
                'preco': p.preco,
                'imagem_url': p.imagem_url,
                'estoque': p.estoque,
                'categoria': {
                    'id': p.categoria.id if p.categoria else None,
                    'nome': p.categoria.nome if p.categoria else None
                }
            })

    return jsonify({'pelucias': pelucias, 'valor_total': f"{valor_total:.2f}"})

@app.route('/colecao/<int:pelucia_id>', methods=['DELETE'])
def remover_do_colecao(pelucia_id):
    item = Colecao.query.filter_by(pelucia_id=pelucia_id).first()
    if not item:
        return jsonify({'erro': 'pelucia não está no colecao'}), 404

    try:
        pelucia = Pelucia.query.get(pelucia_id)
        if pelucia:
            pelucia.estoque += 1
        db.session.delete(item)
        db.session.commit()
        return jsonify({'mensagem': 'pelucia removido do colecao!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': 'Erro ao remover do colecao', 'detalhe': str(e)}), 500

@app.route('/pelucias/usuario/<int:usuario_id>', methods=['GET'])
def pelucias_por_usuario(usuario_id):
    pelucias = Pelucia.query.filter_by(usuario_id=usuario_id).all()
    lista = []
    for p in pelucias:
        lista.append({
            'id': p.id,
            'nome': p.nome,
            'preco': p.preco,
            'imagem_url': p.imagem_url,
            'estoque': p.estoque,
            'categoria': {
                'id': p.categoria.id if p.categoria else None,
                'nome': p.categoria.nome if p.categoria else None
            }
        })
    return jsonify(lista)


@app.route('/pelucias/categoria/<int:categoria_id>', methods=['GET'])
def pelucias_por_categoria(categoria_id):
    pelucias = Pelucia.query.filter_by(categoria_id=categoria_id).all()
    lista = []
    for p in pelucias:
        lista.append({
            'id': p.id,
            'nome': p.nome,
            'preco': p.preco,
            'imagem_url': p.imagem_url,
            'estoque': p.estoque,
            'categoria': {
                'id': p.categoria.id if p.categoria else None,
                'nome': p.categoria.nome if p.categoria else None
            }
        })
    return jsonify(lista)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
