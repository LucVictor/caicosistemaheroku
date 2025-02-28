from ..main import *
@app.route('/vendas/erros', methods=["GET", "POST"])
@access_level_required(1)
@login_required
def vendas_erros():
    erros = Erros_Vendas.query.filter(
            Erros_Vendas.data_do_erro >= primeiro_dia_mes(),
            Erros_Vendas.data_do_erro <= ultimo_dia_mes()).order_by(
            Erros_Vendas.data_do_erro.desc()).all()

    erros_por_funcionario = db.session.query(
        Erros_Vendas.erro_funcionario,
        func.sum(Erros_Vendas.quantidade_de_erros).label('total_erros'),

    ).filter(
        Erros_Vendas.data_do_erro >= primeiro_dia_mes(),
        Erros_Vendas.data_do_erro <= ultimo_dia_mes()
    ).group_by(
        Erros_Vendas.erro_funcionario
    ).all()

    total_erros = 0
    for i in erros_por_funcionario:
        total_erros += i.total_erros

    subquery = db.session.query(
        Entrega.motorista,
        Entrega.rota,
        Entrega.resultado_tempo,
        Entrega.quantidade_de_entregas,
        Entrega.data_da_entrega,
        Entrega.reentregas,
        Entrega.conferente
    ).filter(
        Entrega.data_da_entrega.between(primeiro_dia_mes(), ultimo_dia_mes())
    ).subquery()

    total_entregas = func.sum(subquery.c.quantidade_de_entregas)
    resultados_entregas = db.session.query(
        subquery.c.conferente,
        total_entregas.label('total_entregas')
    ).group_by(
        subquery.c.conferente
    ).order_by(
        subquery.c.conferente.asc()
    ).all()

    total_de_entregas = 0
    for i in resultados_entregas:
        total_de_entregas += i.total_entregas

    total_erros = 0
    for i in erros_por_funcionario:
        total_erros += i.total_erros

    return render_template("/vendas/erros.html", mes=mes_atual(), erros=erros,
                           erros_por_funcionario=erros_por_funcionario, total_erros=total_erros, total_de_entregas=total_de_entregas )




@app.route('/vendas/erros_relatorio', methods=["GET", "POST"])
@access_level_required(1)
@login_required
def relatorio_vendas_erros():
    if request.method == 'POST':
        data_inicial = request.form['data_inicial']
        data_final = request.form['data_final']
        erros = Erros_Vendas.query.filter(
            Erros_Vendas.data_do_erro >= data_inicial,
            Erros_Vendas.data_do_erro <= data_final).order_by(
            Erros_Vendas.data_do_erro.desc()).all()

        erros_por_funcionario = db.session.query(
            Erros_Vendas.erro_funcionario,
            func.sum(Erros_Vendas.quantidade_de_erros).label('total_erros'),

        ).filter(
            Erros_Vendas.data_do_erro >= data_inicial,
            Erros_Vendas.data_do_erro <= data_final
        ).group_by(
            Erros_Vendas.erro_funcionario
        ).all()

        total_erros = 0
        for i in erros_por_funcionario:
            total_erros += i.total_erros

        subquery = db.session.query(
            Entrega.quantidade_de_entregas
        ).filter(
            Entrega.data_da_entrega.between(data_inicial, data_final)
        ).subquery()

        total_entregas = db.session.query(
        func.sum(Entrega.quantidade_de_entregas).label('total_entregas')
        ).filter(
        Entrega.data_da_entrega.between(data_inicial, data_final)
        ).scalar()

        total_de_entregas = 0
        for i in resultados_entregas:
            total_de_entregas += i.total_entregas

        return render_template("/vendas/relatorio.html", mes=mes_atual(), erros=erros,
                               erros_por_funcionario=erros_por_funcionario, total_erros=total_erros, total_de_entregas=total_de_entregas,
                               data_inicial=formatar_data(data_inicial), data_final=formatar_data(data_final))
    return render_template('/vendas/relatorio.html')

@app.route('/vendas/cadastrar_erro', methods=["GET", "POST"])
@access_level_required(1)
@login_required
def cadastrar_vendas_erro():
    funcionarios = Funcionarios.query.all()
    if request.method == "POST":
        data_do_erro = request.form["data_do_erro"]
        erro_funcionario = request.form['erro_funcionario']
        erro_cliente = request.form['erro_cliente']
        quantidade_de_erros = request.form['quantidade_de_erros']
        motorista_da_entrega = request.form['motorista_da_entrega']
        produto_erro = request.form['produto_erro']
        descricao_do_erro = request.form['descricao_do_erro']
        criador = current_user.username
        erro = Erros_Vendas(data_do_erro=data_do_erro, erro_funcionario=erro_funcionario,
                            quantidade_de_erros=quantidade_de_erros, erro_cliente=erro_cliente,
                            produto_erro=produto_erro,
                            motorista_da_entrega=motorista_da_entrega, descricao_do_erro=descricao_do_erro,
                            criador=criador)
        db.session.add(erro)
        db.session.commit()
        return redirect(url_for("vendas_erros"))
    return render_template("/vendas/cadastrar_erro.html", funcionarios=funcionarios)


@app.route('/vendas/deletar/<int:erro_id>', methods=["post", 'get'])
@login_required
def deletar_erro_venda(erro_id):
    erro = Erros_Vendas.query.get_or_404(erro_id)
    db.session.delete(erro)
    db.session.commit()
    return redirect(url_for('vendas_erros'))


@app.route('/vendas/editar_erro/<int:erro_id>', methods=["GET", "POST"])
@login_required
def vendas_editar_erro(erro_id):
    erros = Erros_Vendas.query.get_or_404(erro_id)
    funcionarios = Funcionarios.query.all()
    rotas = Rotas.query.all()
    if request.method == "POST":
        data_do_erro = request.form["data_do_erro"]
        erro_funcionario = request.form['erro_funcionario']
        erro_cliente = request.form['erro_cliente']
        quantidade_de_erros = request.form['quantidade_de_erros']
        motorista_da_entrega = request.form['motorista_da_entrega']
        produto_erro = request.form['produto_erro']
        descricao_do_erro = request.form['descricao_do_erro']
        criador = current_user.username

        erros.data_do_erro = data_do_erro
        erros.erro_funcionario = erro_funcionario
        erros.quantidade_de_erros = quantidade_de_erros
        erros.erro_cliente = erro_cliente
        erros.produto_erro = produto_erro
        erros.motorista_da_entrega = motorista_da_entrega
        erros.descricao_do_erro = descricao_do_erro
        erros.criador = criador

        db.session.add(erros)
        db.session.commit()
        return redirect(url_for("vendas_erros"))
    return render_template('/vendas/editar_erro.html', erros=erros, funcionarios=funcionarios, rotas=rotas)

@app.route('/vendas/comparar_erros', methods=['GET','POST'])
def vendas_erros_comparar():
    if request.method == "POST":
        data_inicial_1 = request.form["data_inicial1"]
        data_final_1 = request.form["data_final1"]
        data_inicial_2 = request.form["data_inicial2"]
        data_final_2 = request.form["data_final2"]
        erros_por_funcionario = {}
        total_erros_periodo_1 = 0
        total_erros_periodo_2 = 0
        resultados_periodo_1 = db.session.query(
            Erros_Vendas.erro_funcionario,
            db.func.sum(Erros_Vendas.quantidade_de_erros).label('total_erros')
        ).filter(
            Erros_Vendas.data_do_erro.between(data_inicial_1, data_final_1)
        ).group_by(Erros_Vendas.erro_funcionario).all()

        # Obter erros do período 2
        resultados_periodo_2 = db.session.query(
            Erros_Vendas.erro_funcionario,
            db.func.sum(Erros_Vendas.quantidade_de_erros).label('total_erros')
        ).filter(
            Erros_Vendas.data_do_erro.between(data_inicial_2, data_final_2)
        ).group_by(Erros_Vendas.erro_funcionario).all()

        # Agrupar resultados e calcular totais
        for resultado in resultados_periodo_1:
            funcionario = resultado.erro_funcionario
            total1 = resultado.total_erros
            total_erros_periodo_1 += total1
            if funcionario not in erros_por_funcionario:
                erros_por_funcionario[funcionario] = {'total1': total1, 'total2': 0}
            else:
                erros_por_funcionario[funcionario]['total1'] = total1

        for resultado in resultados_periodo_2:
            funcionario = resultado.erro_funcionario
            total2 = resultado.total_erros
            total_erros_periodo_2 += total2
            if funcionario not in erros_por_funcionario:
                erros_por_funcionario[funcionario] = {'total1': 0, 'total2': total2}
            else:
                erros_por_funcionario[funcionario]['total2'] = total2

        subquery = db.session.query(
            Entrega.quantidade_de_entregas
        ).filter(
            Entrega.data_da_entrega.between(data_inicial_1, data_final_1)
        ).subquery()

        total_entregas = func.sum(subquery.c.quantidade_de_entregas)
        resultados_entregas = db.session.query(
            subquery.c.quantidade_de_entregas,
            total_entregas.label('total_entregas')
        ).all()

        total_de_entregas = 0
        for i in resultados_entregas:
            total_de_entregas += i.total_entregas



        subquery2 = db.session.query(
            Entrega.quantidade_de_entregas
        ).filter(
            Entrega.data_da_entrega.between(data_inicial_2, data_final_2)
        ).subquery()

        total_entregas2 = func.sum(subquery2.c.quantidade_de_entregas)
        resultados_entregas2 = db.session.query(
            subquery2.c.quantidade_de_entregas,
            total_entregas2.label('total_entregas')
        ).all()

        total_de_entregas2 = 0
        for i in resultados_entregas2:
            total_de_entregas2 += i.total_entregas
        array_erros=[]
        array_erros.append(total_erros_periodo_1)
        array_erros.append(total_erros_periodo_2)

        return render_template('vendas/comparar_erros.html', array_erros=array_erros,  erros_por_funcionario=erros_por_funcionario,
                               data_inicial1=formatar_data(data_inicial_1),
                               data_final1=formatar_data(data_final_1), data_inicial2=formatar_data(data_inicial_2),
                               data_final2=formatar_data(data_final_2), total_erros_periodo_1=total_erros_periodo_1,
                           total_erros_periodo_2=total_erros_periodo_2, calcular_porcentagem=calcular_porcentagem, total_de_entregas=total_de_entregas, total_de_entregas2=total_de_entregas2)
    return render_template('vendas/comparar_erros.html')

