from ..main import *


@app.route('/entregas/', methods=['GET'])
@login_required
@access_level_required(1)
def entregas_index():
    subquery = db.session.query(
        Entrega.motorista,
        Entrega.rota,
        Entrega.resultado_tempo,
        Entrega.quantidade_de_entregas,
        Entrega.data_da_entrega,
        Entrega.reentregas
    ).filter(
        Entrega.data_da_entrega.between(primeiro_dia_mes(), ultimo_dia_mes())
    ).subquery()

    total_positivo = func.count(case((subquery.c.resultado_tempo == 'Positivo', 1)))
    total_negativo = func.count(case((subquery.c.resultado_tempo == 'Negativo', 1)))
    total_sum = total_positivo - total_negativo
    total_entregas = func.sum(subquery.c.quantidade_de_entregas)
    total_reentregas = func.sum(subquery.c.reentregas)

    resultados = db.session.query(
        subquery.c.motorista,
        total_positivo.label('total_positivo'),
        total_negativo.label('total_negativo'),
        total_sum.label('total_sum')
    ).group_by(
        subquery.c.motorista
    ).order_by(
        total_sum.desc()
    ).all()

    resultados_entregas = db.session.query(
        subquery.c.rota,
        total_entregas.label('total_entregas'),
        total_reentregas.label('total_reentregas')
    ).group_by(
        subquery.c.rota
    ).order_by(
        total_entregas.desc()
    ).all()

    entregas = db.session.query(Entrega).filter(
        Entrega.data_da_entrega.between(primeiro_dia_mes(), ultimo_dia_mes())
    ).order_by(
        Entrega.data_da_entrega.desc()
    ).all()

    mes = mes_atual()
    rotas = Rotas.query.all()
    total_de_entregas = 0
    for i in resultados_entregas:
        total_de_entregas += i.total_entregas
    total_de_reentregas = 0
    for i in resultados_entregas:
        total_de_reentregas += i.total_reentregas

    total_dias = db.session.query(Entrega).filter(
        Entrega.data_da_entrega.between(primeiro_dia_mes(), ultimo_dia_mes())
    ).order_by(
        Entrega.data_da_entrega.desc()
    ).all()
    a = 0
    b = 0
    for i in total_dias:
        if i.data_da_entrega != a:
            a = i.data_da_entrega
            b = b + 1


    return render_template('entregas/index.html', total_de_reentregas=total_de_reentregas,
                           total_de_entregas=total_de_entregas, mes=mes, rotas=rotas, entregas=entregas,
                           data_agora=data_agora(), b=b,
                           resultados=resultados
                           , resultados_entregas=resultados_entregas, calcular_porcentagem=calcular_porcentagem)


@app.route('/entregas/relatorio', methods=['get'])
@login_required
@access_level_required(1)
def entregas_relatorio():
    return render_template('entregas/relatorio.html')


@app.route('/entregas/emitir_relatorio', methods=['POST'])
@login_required
@access_level_required(1)
def entregas_emitir_relatorio():
    data_inicial = request.form['data_inicial']
    data_final = request.form['data_final']
    subquery = db.session.query(
        Entrega.motorista,
        Entrega.rota,
        Entrega.resultado_tempo,
        Entrega.quantidade_de_entregas,
        Entrega.data_da_entrega,
        Entrega.reentregas
    ).filter(
        Entrega.data_da_entrega.between(data_inicial, data_final)
    ).subquery()

    total_positivo = func.count(case((subquery.c.resultado_tempo == 'Positivo', 1)))
    total_negativo = func.count(case((subquery.c.resultado_tempo == 'Negativo', 1)))
    total_sum = total_positivo - total_negativo
    total_entregas = func.sum(subquery.c.quantidade_de_entregas)
    total_reentregas = func.sum(subquery.c.reentregas)

    resultados = db.session.query(
        subquery.c.motorista,
        total_positivo.label('total_positivo'),
        total_negativo.label('total_negativo'),
        total_sum.label('total_sum')
    ).group_by(
        subquery.c.motorista
    ).order_by(
        total_sum.desc()
    ).all()

    resultados_entregas = db.session.query(
        subquery.c.rota,
        total_entregas.label('total_entregas'),
        total_reentregas.label('total_reentregas')
    ).group_by(
        subquery.c.rota
    ).order_by(
        total_entregas.desc()
    ).all()

    entregas = db.session.query(Entrega).filter(
        Entrega.data_da_entrega.between(data_inicial, data_final)
    ).order_by(
        Entrega.data_da_entrega.desc()
    ).all()

    total_de_entregas = 0
    for i in resultados_entregas:
        total_de_entregas += i.total_entregas
    total_de_reentregas = 0
    for i in resultados_entregas:
        total_de_reentregas += i.total_reentregas
    mes = mes_atual()

    total_dias = db.session.query(Entrega).filter(
        Entrega.data_da_entrega.between(data_inicial, data_final)
    ).order_by(
        Entrega.data_da_entrega.desc()
    ).all()
    a = 0
    b = 0
    for i in total_dias:
        if i.data_da_entrega != a:
            a = i.data_da_entrega
            b = b + 1

    return render_template('entregas/emitir_relatorio.html', total_de_reentregas=total_de_reentregas,
                           total_de_entregas=total_de_entregas, mes=mes,
                           entregas=entregas, data_agora=data_agora(), b=b, resultados=resultados,
                           resultados_entregas=resultados_entregas, data_inicial=formatar_data(data_inicial),
                           data_final=formatar_data(data_final))


@app.route('/entregas/comparar_entregas', methods=['GET', 'POST'])
@login_required
@access_level_required(1)
def entregar_comparar_entregas():
    entregas_por_rota = {}
    total_entregas_periodo_1 = 0
    total_reentregas_periodo_1 = 0
    total_entregas_periodo_2 = 0
    total_reentregas_periodo_2 = 0
    if request.method == 'POST':
        data_inicial_1 = request.form['data_inicial1']
        data_final_1 = request.form['data_final1']
        data_inicial_2 = request.form['data_inicial2']
        data_final_2 = request.form['data_final2']

        # Obter entregas do período 1
        resultados_periodo_1 = db.session.query(
            Entrega.rota,
            db.func.sum(Entrega.quantidade_de_entregas).label('total_entregas'),
            db.func.sum(Entrega.reentregas).label('total_reentregas')
        ).filter(
            Entrega.data_da_entrega.between(data_inicial_1, data_final_1)
        ).group_by(Entrega.rota).all()

        # Obter entregas do período 2
        resultados_periodo_2 = db.session.query(
            Entrega.rota,
            db.func.sum(Entrega.quantidade_de_entregas).label('total_entregas'),
            db.func.sum(Entrega.reentregas).label('total_reentregas')
        ).filter(
            Entrega.data_da_entrega.between(data_inicial_2, data_final_2)
        ).group_by(Entrega.rota).all()

        # Agrupar resultados e calcular totais
        for resultado in resultados_periodo_1:
            rota = resultado.rota
            total_entregas_1 = resultado.total_entregas or 0
            total_reentregas_1 = resultado.total_reentregas or 0
            total_entregas_periodo_1 += total_entregas_1
            total_reentregas_periodo_1 += total_reentregas_1
            if rota not in entregas_por_rota:
                entregas_por_rota[rota] = {'total_entregas_1': total_entregas_1,
                                           'total_reentregas_1': total_reentregas_1,
                                           'total_entregas_2': 0, 'total_reentregas_2': 0}
            else:
                entregas_por_rota[rota]['total_entregas_1'] = total_entregas_1
                entregas_por_rota[rota]['total_reentregas_1'] = total_reentregas_1

        for resultado in resultados_periodo_2:
            rota = resultado.rota
            total_entregas_2 = resultado.total_entregas or 0
            total_reentregas_2 = resultado.total_reentregas or 0
            total_entregas_periodo_2 += total_entregas_2
            total_reentregas_periodo_2 += total_reentregas_2
            if rota not in entregas_por_rota:
                entregas_por_rota[rota] = {'total_entregas_1': 0, 'total_reentregas_1': 0,
                                           'total_entregas_2': total_entregas_2,
                                           'total_reentregas_2': total_reentregas_2}
            else:
                entregas_por_rota[rota]['total_entregas_2'] = total_entregas_2
                entregas_por_rota[rota]['total_reentregas_2'] = total_reentregas_2
        arry_entregas = []
        arry_reentregas = []
        arry_reentregas.append(total_reentregas_periodo_1)
        arry_reentregas.append(total_reentregas_periodo_2)
        arry_entregas.append(total_entregas_periodo_1)
        arry_entregas.append(total_entregas_periodo_2)
        return render_template('entregas/comparar_entregas.html',
                               arry_reentregas=arry_reentregas,
                               arry_entregas=arry_entregas,
                               entregas_por_rota=entregas_por_rota,
                               total_entregas_periodo_1=total_entregas_periodo_1,
                               total_reentregas_periodo_1=total_reentregas_periodo_1,
                               total_entregas_periodo_2=total_entregas_periodo_2,
                               total_reentregas_periodo_2=total_reentregas_periodo_2,
                               data_inicial1=formatar_data(data_inicial_1), data_inicial2=formatar_data(data_inicial_2),
                               data_final1=formatar_data(data_final_1), data_final2=formatar_data(data_final_2),
                               calcular_porcentagem=calcular_porcentagem)

    return render_template('entregas/comparar_entregas.html')


@app.route('/entregas/cadastrar', methods=['GET', 'POST'])
@login_required
@access_level_required(1)
def entrega_cadastrar():
    if request.method == 'POST':
        data_da_entrega = datetime.strptime(request.form['data_da_entrega'], '%Y-%m-%d').date()
        motorista = request.form['motorista']
        ajudante = request.form['ajudante']
        conferente = request.form['conferente']
        rota = request.form['rota']
        quantidade_de_entregas = int(request.form['quantidade_de_entregas'])
        tempo_total = datetime.strptime(request.form['tempo_total'], '%H:%M').time()
        reentregas = int(request.form['reentregas'])
        entreganrealizadas = int(request.form['entreganrealizadas'])
        tempo_medio_total = hora_para_segundo(tempo_total) / quantidade_de_entregas
        tempo_medio_total = segundos_para_hora(tempo_medio_total)

        tempo_total_entrega = datetime.strptime(request.form['tempo_total_entrega'], '%H:%M').time()
        tempo_medio_entrega = hora_para_segundo(tempo_total_entrega) / quantidade_de_entregas
        tempo_medio_entrega = segundos_para_hora(tempo_medio_entrega)

        rota_media = Rotas.query.filter_by(rota=rota).first()
        if hora_para_segundo(rota_media.tempo_medio_rota) <= hora_para_segundo(tempo_medio_entrega):
            resultado_tempo = "Negativo"
        else:
            resultado_tempo = "Positivo"

        entrega = Entrega(
            data_da_entrega=data_da_entrega,
            motorista=motorista,
            ajudante=ajudante,
            conferente=conferente,
            rota=rota,
            quantidade_de_entregas=quantidade_de_entregas,
            tempo_total=tempo_total,
            tempo_total_entrega=tempo_total_entrega,
            tempo_medio_total=tempo_medio_total,
            tempo_medio_entrega=tempo_medio_entrega,
            resultado_tempo=resultado_tempo,
            reentregas=reentregas,
            entreganrealizadas=entreganrealizadas
        )
        db.session.add(entrega)
        db.session.commit()
        recalcular_rotas(rota)
        return redirect("/entregas/")
    rotas_lista = Rotas.query.all()
    funcionarios = Funcionarios.query.all()
    return render_template("/entregas/cadastrar_entrega.html", rotas_lista=rotas_lista, funcionarios=funcionarios)


total_reentregas_periodo_2 = 0


@app.route('/entregas/deletar_entrega/<int:entrega_id>', methods=["post"])
@login_required
def deletar_entrega(entrega_id):
    entrega = Entrega.query.get_or_404(entrega_id)
    db.session.delete(entrega)
    db.session.commit()
    return redirect(url_for('entregas_index'))


@app.route('/entregas/calcular', methods=['GET', 'POST'])
def calcular_medias_rotas():
    rotas_tempo = Rotas.query.all()
    if request.method == 'POST':
        sum_tempo_medio_entrega = db.session.query(
            Entrega.rota,
            func.sum(
                (func.hour(Entrega.tempo_medio_entrega) * 3600) +
                (func.minute(Entrega.tempo_medio_entrega) * 60) +
                func.second(Entrega.tempo_medio_entrega)
            ).label('sum_tempo_medio_entrega'),
            func.count(Entrega.id).label('total_entregas')
        ).group_by(
            Entrega.rota
        ).all()

        # Update the Rotas table with the average delivery time
        for sum_tempo in sum_tempo_medio_entrega:
            rota = Rotas.query.filter_by(rota=sum_tempo.rota).first()
            if rota and sum_tempo.total_entregas > 0:
                total_seconds = int(sum_tempo.sum_tempo_medio_entrega / sum_tempo.total_entregas)
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60
                rota.tempo_medio_rota = time(hours, minutes, seconds)
                db.session.commit()

    return render_template('/entregas/calcular_medias_rotas.html', rotas_tempo=rotas_tempo)


@app.route('/entregas/rotas', methods=['GET', 'POST'])
def rotas_listagem():
    rotas_lista = Rotas.query.all()
    return render_template("/entregas/rotas.html", rotas_lista=rotas_lista)


@app.route('/entregas/rotas_cadastrar', methods=['GET', 'POST'])
def rotas_cadastrar():
    try:
        if request.method == 'POST':
            rota = request.form['rota']
            tempo_medio = request.form['tempo_medio']
            atualizar = Rotas.query.filter_by(rota=rota).first()
            if atualizar:
                atualizar.tempo_medio_rota = datetime.strptime(tempo_medio, '%H:%M:%S').time()
                db.session.commit()
                return render_template("/entregas/rotas_cadastrar.html", erro='Rota atualizada')
            nova_rota = Rotas(rota=rota, tempo_medio_rota=datetime.strptime(tempo_medio, '%H:%M:%S').time())
            db.session.add(nova_rota)
            db.session.commit()
            return render_template("/entregas/rotas_cadastrar.html", erro='Rota cadastrada')
    except sqlalchemy.exc.IntegrityError:
        db.session.rollback()
        return render_template("/entregas/rotas_cadastrar.html", erro='Erro ao cadastrar')

    return render_template("/entregas/rotas_cadastrar.html")


@app.route('/entregas/erros', methods=["GET", "POST"])
@access_level_required(1)
@login_required
def entregas_erros():
    erros = Erros_Logistica.query.filter(
        Erros_Logistica.data_do_erro >= primeiro_dia_mes(),
        Erros_Logistica.data_do_erro <= ultimo_dia_mes()
    ).order_by(
        Erros_Logistica.data_do_erro.desc()).all()
    erros_por_funcionario = db.session.query(
        Erros_Logistica.erro_funcionario,
        func.sum(Erros_Logistica.quantidade_de_erros).label('total_erros'),

    ).filter(
        Erros_Logistica.data_do_erro >= primeiro_dia_mes(),
        Erros_Logistica.data_do_erro <= ultimo_dia_mes()
    ).group_by(
        Erros_Logistica.erro_funcionario
    ).all()

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
    total_array_resultados_entregas = len(resultados_entregas)
    return render_template("/entregas/erros.html", mes=mes_atual(),
                           total_array_resultados_entregas=total_array_resultados_entregas, erros=erros,
                           resultados_entregas=resultados_entregas,
                           erros_por_funcionario=erros_por_funcionario, total_erros=total_erros,
                           total_de_entregas=total_de_entregas, calcular_porcentagem=calcular_porcentagem)


@app.route('/entregas/erros_relatorio', methods=["GET", "POST"])
@access_level_required(1)
@login_required
def entregas_erros_relatorio():
    if request.method == "POST":
        data_inicial = request.form["data_inicial"]
        data_final = request.form["data_final"]
        erros = Erros_Logistica.query.filter(
            Erros_Logistica.data_do_erro >= data_inicial,
            Erros_Logistica.data_do_erro <= data_final
        ).order_by(
            Erros_Logistica.data_do_erro.desc()).all()
        erros_por_funcionario = db.session.query(
            Erros_Logistica.erro_funcionario,
            func.sum(Erros_Logistica.quantidade_de_erros).label('total_erros')
        ).filter(
            Erros_Logistica.data_do_erro >= data_inicial,
            Erros_Logistica.data_do_erro <= data_final
        ).group_by(
            Erros_Logistica.erro_funcionario
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
            Entrega.data_da_entrega.between(data_inicial, data_final)
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
        total_array_resultados_entregas = len(resultados_entregas)
        return render_template("/entregas/emitir_erro_relatorio.html",
                               total_array_resultados_entregas=total_array_resultados_entregas, mes=mes_atual(),
                               erros=erros, resultados_entregas=resultados_entregas,
                               erros_por_funcionario=erros_por_funcionario, total_erros=total_erros,
                               data_inicial=formatar_data(data_inicial), data_final=formatar_data(data_final),
                               total_de_entregas=total_de_entregas)
    return render_template('entregas/relatorio_erro.html')


@app.route('/entregas/comparar_erros', methods=['GET', 'POST'])
def entregas_erros_comparar():
    if request.method == "POST":
        data_inicial_1 = request.form["data_inicial1"]
        data_final_1 = request.form["data_final1"]
        data_inicial_2 = request.form["data_inicial2"]
        data_final_2 = request.form["data_final2"]
        erros_por_funcionario = {}
        total_erros_periodo_1 = 0
        total_erros_periodo_2 = 0
        resultados_periodo_1 = db.session.query(
            Erros_Logistica.erro_funcionario,
            db.func.sum(Erros_Logistica.quantidade_de_erros).label('total_erros')
        ).filter(
            Erros_Logistica.data_do_erro.between(data_inicial_1, data_final_1)
        ).group_by(Erros_Logistica.erro_funcionario).all()

        # Obter erros do período 2
        resultados_periodo_2 = db.session.query(
            Erros_Logistica.erro_funcionario,
            db.func.sum(Erros_Logistica.quantidade_de_erros).label('total_erros')
        ).filter(
            Erros_Logistica.data_do_erro.between(data_inicial_2, data_final_2)
        ).group_by(Erros_Logistica.erro_funcionario).all()

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
            if i.total_entregas:
                total_de_entregas2 += i.total_entregas
        array_erros = []
        array_erros.append(total_erros_periodo_1)
        array_erros.append(total_erros_periodo_2)
        return render_template('entregas/comparar_erros.html', array_erros=array_erros,
                               erros_por_funcionario=erros_por_funcionario,
                               data_inicial1=formatar_data(data_inicial_1),
                               data_final1=formatar_data(data_final_1), data_inicial2=formatar_data(data_inicial_2),
                               data_final2=formatar_data(data_final_2), total_erros_periodo_1=total_erros_periodo_1,
                               total_erros_periodo_2=total_erros_periodo_2, calcular_porcentagem=calcular_porcentagem,
                               total_de_entregas=total_de_entregas, total_de_entregas2=total_de_entregas2)
    return render_template('entregas/comparar_erros.html')


@app.route('/entregas/cadastrar_erro', methods=["GET", "POST"])
@access_level_required(1)
@login_required
def cadastrar_entregas_erro():
    funcionarios = Funcionarios.query.all()
    rotas = Rotas.query.all()
    if request.method == "POST":
        data_do_erro = request.form["data_do_erro"]
        erro_funcionario = request.form['erro_funcionario']
        erro_cliente = request.form['erro_cliente']
        quantidade_de_erros = request.form['quantidade_de_erros']
        motorista_da_entrega = request.form['motorista_da_entrega']
        produto_erro = request.form['produto_erro']
        rota_da_entrega = request.form['rota_da_entrega']
        descricao_do_erro = request.form['descricao_do_erro']
        criador = current_user.username
        erro = Erros_Logistica(data_do_erro=data_do_erro, erro_funcionario=erro_funcionario,
                               quantidade_de_erros=quantidade_de_erros, erro_cliente=erro_cliente,
                               produto_erro=produto_erro,
                               motorista_da_entrega=motorista_da_entrega, descricao_do_erro=descricao_do_erro,
                               rota_da_entrega=rota_da_entrega, criador=criador)
        db.session.add(erro)
        db.session.commit()
        return redirect(url_for("cadastrar_entregas_erro"))
    return render_template("/entregas/cadastrar_erro.html", funcionarios=funcionarios, rotas=rotas)


@app.route('/entregas/deletar_erro/<int:erro_id>', methods=["post", 'get'])
@login_required
def deletar_erro_entrega(erro_id):
    erro = Erros_Logistica.query.get_or_404(erro_id)
    db.session.delete(erro)
    db.session.commit()
    return redirect(url_for('entregas_erros'))


@app.route('/entregas/editar_erro/<int:erro_id>', methods=["GET", "POST"])
@login_required
def entrega_editar(erro_id):
    erros = Erros_Logistica.query.get_or_404(erro_id)
    funcionarios = Funcionarios.query.all()
    rotas = Rotas.query.all()
    if request.method == "POST":
        data_do_erro = request.form["data_do_erro"]
        erro_funcionario = request.form['erro_funcionario']
        erro_cliente = request.form['erro_cliente']
        quantidade_de_erros = request.form['quantidade_de_erros']
        motorista_da_entrega = request.form['motorista_da_entrega']
        produto_erro = request.form['produto_erro']
        rota_da_entrega = request.form['rota_da_entrega']
        descricao_do_erro = request.form['descricao_do_erro']
        criador = current_user.username

        erros.data_do_erro = data_do_erro
        erros.erro_funcionario = erro_funcionario
        erros.quantidade_de_erros = quantidade_de_erros
        erros.erro_cliente = erro_cliente
        erros.produto_erro = produto_erro
        erros.motorista_da_entrega = motorista_da_entrega
        erros.descricao_do_erro = descricao_do_erro
        erros.rota_da_entrega = rota_da_entrega
        erros.criador = criador

        db.session.add(erros)
        db.session.commit()
        return redirect(url_for("entregas_erros"))
    return render_template('/entregas/editar_erro.html', erros=erros, funcionarios=funcionarios, rotas=rotas)
