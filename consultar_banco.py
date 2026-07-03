# -*- coding: utf-8 -*-
from app import create_app
from app.models import Membro, Usuario

app = create_app()

with app.app_context():
    print("=" * 60)
    print("        CONSULTA AO BANCO DE DADOS")
    print("=" * 60)

    total = Membro.query.count()
    print(f"\nTotal de membros: {total}")
    print("-" * 60)

    membros = Membro.query.order_by(Membro.nome).all()
    if membros:
        print(f"{'ID':<4} {'NOME':<25} {'EMAIL':<30} {'CIDADE':<15} {'ATIVO':<6}")
        print("-" * 80)
        for m in membros:
            ativo = "Sim" if m.ativo else "Nao"
            print(f"{m.id:<4} {m.nome:<25} {m.email:<30} {m.cidade:<15} {ativo:<6}")
    else:
        print("Nenhum membro cadastrado.")

    print("-" * 60)
    ativos = Membro.query.filter_by(ativo=True).count()
    inativos = total - ativos
    print(f"\nMembros ativos: {ativos}")
    print(f"Membros inativos: {inativos}")

    print("\n" + "=" * 60)
    print("        USUARIOS DO SISTEMA")
    print("=" * 60)
    usuarios = Usuario.query.all()
    if usuarios:
        for u in usuarios:
            print(f"Usuario: {u.username} (admin: {u.is_admin})")
    else:
        print("Nenhum usuario cadastrado.")

    print("\nConsulta finalizada!")
