# -*- coding: utf-8 -*-
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
import os
from werkzeug.utils import secure_filename
from datetime import date
from app import db
from app.models import Membro
from app.forms import MembroForm, MembroPublicoForm

membros_bp = Blueprint('membros', __name__)


@membros_bp.route('/')
@login_required
def index():
    return redirect(url_for('membros.dashboard'))


@membros_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard com estatísticas"""
    total = Membro.query.count()
    ativos = Membro.query.filter_by(ativo=True).count()
    inativos = total - ativos

    # Aniversariantes do mês
    from datetime import date
    mes_atual = date.today().month
    aniversariantes = Membro.query.filter(
        db.extract('month', Membro.data_nascimento) == mes_atual
    ).count()

    # Últimos membros cadastrados
    ultimos = Membro.query.order_by(Membro.data_cadastro.desc()).limit(5).all()

    return render_template(
        'dashboard.html',
        total=total,
        ativos=ativos,
        inativos=inativos,
        aniversariantes=aniversariantes,
        ultimos=ultimos
    )


@membros_bp.route('/membros')
@login_required
def listar_membros():
    """Lista todos os membros cadastrados com busca e paginação"""
    pagina = request.args.get('pagina', 1, type=int)
    busca = request.args.get('busca', '').strip()

    if pagina < 1:
        pagina = 1

    query = Membro.query

    if busca:
        query = query.filter(
            db.or_(
                Membro.nome.ilike(f'%{busca}%'),
                Membro.email.ilike(f'%{busca}%'),
                Membro.cidade.ilike(f'%{busca}%'),
                Membro.telefone.ilike(f'%{busca}%')
            )
        )

    query = query.order_by(Membro.nome.asc())
    membros_paginados = query.paginate(
        page=pagina, per_page=12, error_out=False
    )

    return render_template(
        'membros.html',
        membros=membros_paginados,
        busca=busca
    )


@membros_bp.route('/cadastro', methods=['GET', 'POST'])
@login_required
def cadastro():
    """Página de cadastro de novo membro"""
    form = MembroForm()
    if form.validate_on_submit():
        try:
            # Verificar se email já existe
            if Membro.query.filter_by(email=form.email.data).first():
                flash('Este email já está cadastrado.', 'danger')
                return render_template('cadastro.html', form=form)

            novo_membro = Membro(
                nome=form.nome.data,
                email=form.email.data,
                telefone=form.telefone.data,
                data_nascimento=form.data_nascimento.data,
                endereco=form.endereco.data,
                cidade=form.cidade.data,
                estado=form.estado.data,
                ativo=form.ativo.data,
                cadastrado_por_id=current_user.id
            )
            db.session.add(novo_membro)
            db.session.commit()
            flash(f'Membro {novo_membro.nome} cadastrado com sucesso!', 'success')
            return redirect(url_for('membros.ver_membro', id=novo_membro.id))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Erro ao cadastrar membro: {e}')
            flash('Erro ao cadastrar. Verifique os dados e tente novamente.', 'danger')

    return render_template('cadastro.html', form=form)



@membros_bp.route('/cadastre-se', methods=['GET', 'POST'])
def cadastro_publico():
    """Página pública de auto-cadastro para membros (sem login)"""
    form = MembroPublicoForm()
    if form.validate_on_submit():
        try:
            if Membro.query.filter_by(email=form.email.data).first():
                flash('Este email já está cadastrado em nosso sistema.', 'danger')
                return render_template('cadastro_publico.html', form=form)

            novo_membro = Membro(
                nome=form.nome.data,
                email=form.email.data,
                telefone=form.telefone.data,
                data_nascimento=form.data_nascimento.data,
                endereco=form.endereco.data,
                cidade=form.cidade.data,
                estado=form.estado.data,
                ativo=True,
                cadastrado_por_id=None
            )
            db.session.add(novo_membro)
            db.session.commit()
            flash(f'Cadastro realizado com sucesso, {novo_membro.nome}! Em breve entraremos em contato.', 'success')
            return redirect(url_for('membros.cadastro_sucesso'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Erro no auto-cadastro: {e}')
            flash('Erro ao realizar cadastro. Verifique os dados e tente novamente.', 'danger')

    return render_template('cadastro_publico.html', form=form)


@membros_bp.route('/cadastro-sucesso')
def cadastro_sucesso():
    """Página de confirmação de auto-cadastro"""
    return render_template('sucesso_publico.html')




@membros_bp.route('/membro/<int:id>')
@login_required
def ver_membro(id):
    """Visualiza detalhes de um membro"""
    membro = Membro.query.get_or_404(id)
    return render_template('membro_detalhes.html', membro=membro)


@membros_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Edita dados de um membro"""
    membro = Membro.query.get_or_404(id)
    form = MembroForm(obj=membro)

    if form.validate_on_submit():
        try:
            # Verificar email duplicado (se mudou)
            email_existente = Membro.query.filter(
                Membro.email == form.email.data,
                Membro.id != id
            ).first()
            if email_existente:
                flash('Este email já está em uso por outro membro.', 'danger')
                return render_template('editar_membro.html', form=form, membro=membro)

            form.populate_obj(membro)
            db.session.commit()
            flash('Dados atualizados com sucesso!', 'success')
            return redirect(url_for('membros.ver_membro', id=membro.id))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Erro ao editar membro {id}: {e}')
            flash('Erro ao editar. Verifique os dados.', 'danger')

    return render_template('editar_membro.html', form=form, membro=membro)




@membros_bp.route('/upload-foto/<int:id>', methods=['POST'])
@login_required
def upload_foto(id):
    from app import db
    from flask import jsonify
    membro = Membro.query.get_or_404(id)

    if 'foto' not in request.files:
        flash('Nenhum arquivo enviado.', 'danger')
        return redirect(url_for('membros.ver_membro', id=id))

    file = request.files['foto']
    if file.filename == '':
        flash('Nenhum arquivo selecionado.', 'danger')
        return redirect(url_for('membros.ver_membro', id=id))

    if file:
        filename = secure_filename(f'membro_{id}_{file.filename}')
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        membro.foto = f'/static/uploads/{filename}'
        db.session.commit()
        flash('Foto atualizada com sucesso!', 'success')

    return redirect(url_for('membros.ver_membro', id=id))



@membros_bp.route('/deletar/<int:id>', methods=['POST'])
@login_required
def deletar(id):
    """Deleta (ou inativa) um membro"""
    membro = Membro.query.get_or_404(id)
    nome = membro.nome

    # Soft delete: apenas inativa o membro
    membro.ativo = False
    db.session.commit()

    flash(f'Membro {nome} foi desativado.', 'info')
    return redirect(url_for('membros.listar_membros'))


@membros_bp.route('/reativar/<int:id>', methods=['POST'])
@login_required
def reativar(id):
    """Reativa um membro inativo"""
    membro = Membro.query.get_or_404(id)
    membro.ativo = True
    db.session.commit()
    flash(f'Membro {membro.nome} reativado!', 'success')
    return redirect(url_for('membros.ver_membro', id=membro.id))









@membros_bp.route("/bg")
def background_img():
    """Serve a imagem de fundo"""
    from flask import send_from_directory
    import os
    img_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "img")
    return send_from_directory(img_dir, "ovelha.jpg")
