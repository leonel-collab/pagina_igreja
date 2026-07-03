# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import ( FileField, SelectMultipleField, TextAreaField, IntegerField,
    StringField, PasswordField, DateField, SelectField,
    BooleanField, SubmitField, EmailField
)
from wtforms.validators import DataRequired, Email, Length, EqualTo

ESTADOS_BRASIL = [
    ('', 'Selecione um estado'),
    ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'),
    ('AM', 'Amazonas'), ('BA', 'Bahia'), ('CE', 'Ceará'),
    ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'),
    ('GO', 'Goiás'), ('MA', 'Maranhão'), ('MT', 'Mato Grosso'),
    ('MS', 'Mato Grosso do Sul'), ('MG', 'Minas Gerais'),
    ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'),
    ('PE', 'Pernambuco'), ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'),
    ('RN', 'Rio Grande do Norte'), ('RS', 'Rio Grande do Sul'),
    ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'),
    ('SP', 'São Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins'),
]


class MembroForm(FlaskForm):
    nome = StringField(
        'Nome Completo',
        validators=[DataRequired(), Length(min=3, max=100)]
    )
    email = EmailField(
        'Email',
        validators=[DataRequired(), Email(), Length(max=120)]
    )
    telefone = StringField(
        'Telefone',
        validators=[DataRequired(), Length(min=10, max=20)]
    )
    data_nascimento = DateField(
        'Data de Nascimento',
        validators=[DataRequired()],
        format='%Y-%m-%d'
    )
    endereco = StringField(
        'Endereço',
        validators=[DataRequired(), Length(max=200)]
    )
    cidade = StringField(
        'Cidade',
        validators=[DataRequired(), Length(max=50)]
    )
    estado = SelectField(
        'Estado',
        choices=ESTADOS_BRASIL,
        validators=[DataRequired()]
    )
    foto = FileField('Foto do Membro')
    ativo = BooleanField('Membro Ativo', default=True)
    submit = SubmitField('Salvar')


class LoginForm(FlaskForm):
    username = StringField(
        'Usuário',
        validators=[DataRequired(), Length(min=3, max=80)]
    )
    senha = PasswordField(
        'Senha',
        validators=[DataRequired()]
    )
    submit = SubmitField('Entrar')


class CadastroUsuarioForm(FlaskForm):
    username = StringField(
        'Usuário',
        validators=[DataRequired(), Length(min=3, max=80)]
    )
    email = EmailField(
        'Email',
        validators=[DataRequired(), Email()]
    )
    senha = PasswordField(
        'Senha',
        validators=[DataRequired(), Length(min=6, max=100)]
    )
    confirmar_senha = PasswordField(
        'Confirmar Senha',
        validators=[DataRequired(), EqualTo('senha', 'Senhas não conferem')]
    )
    submit = SubmitField('Cadastrar')




class MembroPublicoForm(FlaskForm):
    nome = StringField(
        'Nome Completo',
        validators=[DataRequired(), Length(min=3, max=100)]
    )
    email = EmailField(
        'Email',
        validators=[DataRequired(), Email(), Length(max=120)]
    )
    telefone = StringField(
        'Telefone',
        validators=[DataRequired(), Length(min=10, max=20)]
    )
    data_nascimento = DateField(
        'Data de Nascimento',
        validators=[DataRequired()],
        format='%Y-%m-%d'
    )
    endereco = StringField(
        'Endereço',
        validators=[DataRequired(), Length(max=200)]
    )
    cidade = StringField(
        'Cidade',
        validators=[DataRequired(), Length(max=50)]
    )
    estado = SelectField(
        'Estado',
        choices=ESTADOS_BRASIL,
        validators=[DataRequired()]
    )
    submit = SubmitField('Fazer Cadastro')


class EmailMassaForm(FlaskForm):
    destinatarios = SelectMultipleField(
        'Destinatarios',
        choices=[],
        validators=[DataRequired()]
    )
    assunto = StringField(
        'Assunto',
        validators=[DataRequired(), Length(max=200)]
    )
    mensagem = TextAreaField(
        'Mensagem',
        validators=[DataRequired()],
        render_kw={'rows': 10}
    )
    submit = SubmitField('Enviar Email')


class ConfigEmailForm(FlaskForm):
    servidor = StringField('Servidor SMTP', validators=[DataRequired()])
    porta = IntegerField('Porta', validators=[DataRequired()], default=587)
    usuario = StringField('Usuario', validators=[DataRequired()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Salvar Configuracao')


