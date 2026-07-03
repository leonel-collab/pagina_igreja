# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required
from app import db, mail
from app.models import Membro
from app.forms import EmailMassaForm
from flask_mail import Message

email_bp = Blueprint('email', __name__, url_prefix='/email')

@email_bp.route('/enviar', methods=['GET', 'POST'])
@login_required
def enviar_email():
    form = EmailMassaForm()
    membros = Membro.query.filter_by(ativo=True).order_by(Membro.nome).all()
    form.destinatarios.choices = [(str(m.id), m.nome) for m in membros]

    if form.validate_on_submit():
        try:
            destinatarios_ids = form.destinatarios.data
            assunto = form.assunto.data
            mensagem = form.mensagem.data

            ids_int = [int(id_str) for id_str in destinatarios_ids]
            membros_selecionados = Membro.query.filter(Membro.id.in_(ids_int)).all()

            if not membros_selecionados:
                flash('Nenhum destinatario selecionado.', 'warning')
                return render_template('email_massa.html', form=form)

            tem_config = bool(current_app.config.get('MAIL_USERNAME') and
                             current_app.config.get('MAIL_PASSWORD'))

            if not tem_config:
                nomes = [m.nome for m in membros_selecionados]
                current_app.logger.info(f'SIMULACAO: Email para {len(membros_selecionados)} membro(s): {", ".join(nomes)}')
                flash(f'Email seria enviado para {len(membros_selecionados)} membro(s)! Configure o email no .env.', 'info')
                return redirect(url_for('email.enviar_email'))

            with mail.connect() as conn:
                for membro in membros_selecionados:
                    if membro.email:
                        msg = Message(subject=assunto, recipients=[membro.email], html=mensagem.replace('{{nome}}', membro.nome))
                        conn.send(msg)

            flash(f'Email enviado para {len(membros_selecionados)} membro(s)!', 'success')
            return redirect(url_for('email.enviar_email'))

        except Exception as e:
            current_app.logger.error(f'Erro ao enviar email: {e}')
            flash(f'Erro: {str(e)}', 'danger')

    return render_template('email_massa.html', form=form)
