# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify
from flask_login import login_required
from app.models import Membro

api_bp = Blueprint('api', __name__)


@api_bp.route('/membros')
@login_required
def api_membros():
    """API para obter lista de membros em JSON"""
    membros = Membro.query.all()
    return jsonify([m.to_dict() for m in membros])


@api_bp.route('/membro/<int:id>')
@login_required
def api_membro(id):
    """API para obter dados de um membro específico"""
    membro = Membro.query.get_or_404(id)
    return jsonify(membro.to_dict())


@api_bp.route('/estatisticas')
@login_required
def api_estatisticas():
    """API com estatísticas dos membros"""
    total = Membro.query.count()
    ativos = Membro.query.filter_by(ativo=True).count()
    inativos = total - ativos

    from datetime import date
    mes_atual = date.today().month
    from app import db
    aniversariantes = Membro.query.filter(
        db.extract('month', Membro.data_nascimento) == mes_atual
    ).count()

    return jsonify({
        'total': total,
        'ativos': ativos,
        'inativos': inativos,
        'aniversariantes_mes': aniversariantes
    })

