# -*- coding: utf-8 -*-
from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class Membro(db.Model):
    __tablename__ = 'membros'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    telefone = db.Column(db.String(20), nullable=False)
    data_nascimento = db.Column(db.Date, nullable=False)
    endereco = db.Column(db.String(200), nullable=False)
    cidade = db.Column(db.String(50), nullable=False, index=True)
    estado = db.Column(db.String(2), nullable=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)
    foto = db.Column(db.String(200), nullable=True)  # URL da foto

    # Relacionamento com usuário que cadastrou
    cadastrado_por_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)

    def __repr__(self):
        return f'<Membro {self.nome}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'telefone': self.telefone,
            'data_nascimento': self.data_nascimento.strftime('%d/%m/%Y'),
            'endereco': self.endereco,
            'cidade': self.cidade,
            'estado': self.estado,
            'data_cadastro': self.data_cadastro.strftime('%d/%m/%Y %H:%M'),
            'ativo': self.ativo,
            'idade': self.idade
        }

    @property
    def idade(self):
        today = datetime.now().date()
        return today.year - self.data_nascimento.year - (
            (today.month, today.day) <
            (self.data_nascimento.month, self.data_nascimento.day)
        )

    @property
    def aniversario_proximo(self):
        """Verifica se o aniversário é nos próximos 30 dias"""
        today = datetime.now().date()
        next_birthday = self.data_nascimento.replace(year=today.year)
        if next_birthday < today:
            next_birthday = next_birthday.replace(year=today.year + 1)
        dias_restantes = (next_birthday - today).days
        return dias_restantes <= 30, dias_restantes


class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

    membros_cadastrados = db.relationship('Membro', backref='cadastrado_por', lazy='dynamic')

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    def __repr__(self):
        return f'<Usuario {self.username}>'


@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

