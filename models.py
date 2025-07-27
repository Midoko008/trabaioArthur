from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuario'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    cep = db.Column(db.String(9))
    cpf = db.Column(db.String(14))
    data_nascimento = db.Column(db.Date)
    idade = db.Column(db.Integer)
    senha_hash = db.Column(db.Text)
    tipo = db.Column(db.String(20), default='comum')

    pelucias = db.relationship('Pelucia', backref='usuario')

    @staticmethod
    def calcular_idade(data_nascimento):
        hoje = date.today()
        return hoje.year - data_nascimento.year - ((hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day))

    def to_dict_completo(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'cep': self.cep,
            'cpf': self.cpf,
            'data_nascimento': self.data_nascimento.strftime('%Y-%m-%d') if self.data_nascimento else None,
            'idade': self.idade,
            'tipo': self.tipo
        }

    def to_dict_publico(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'idade': self.idade
        }

class Categoria(db.Model):
    __tablename__ = 'categoria'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)

    pelucias = db.relationship('Pelucia', back_populates='categoria', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Categoria {self.nome}>'

class Pelucia(db.Model):
    __tablename__ = 'pelucia'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    imagem_url = db.Column(db.String(255))
    estoque = db.Column(db.Integer, nullable=False)

    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=True)

    categoria = db.relationship('Categoria', back_populates='pelucias')
    colecao_items = db.relationship('Colecao', back_populates='pelucia', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Pelucia {self.nome}>'

class Colecao(db.Model):
    __tablename__ = 'colecao'

    id = db.Column(db.Integer, primary_key=True)
    pelucia_id = db.Column(db.Integer, db.ForeignKey('pelucia.id'), nullable=False)

    pelucia = db.relationship('Pelucia', back_populates='colecao_items')

    def __repr__(self):
        return f'<Colecao pelucia_id={self.pelucia_id}>'
