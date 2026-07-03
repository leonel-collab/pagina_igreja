# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import Usuario
from app.forms import LoginForm

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if current_user.is_authenticated:
        return redirect(url_for('membros.listar_membros'))

    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(username=form.username.data).first()
        if usuario and usuario.check_senha(form.senha.data):
            login_user(usuario)
            next_page = request.args.get('next')
            flash(f'Bem-vindo, {usuario.username}!', 'success')
            return redirect(next_page or url_for('membros.listar_membros'))
        flash('Usuário ou senha inválidos.', 'danger')
        return redirect(url_for('auth.login'))

    return render_template('login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """Efetua logout"""
    logout_user()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('auth.login'))

