from ..main import *
@app.route('/avarias/', methods=['GET'])
@login_required
def index_avarias():
    avarias = Produto_Avaria.query.filter(Produto_Avaria.data_de_insercao >= primeiro_dia_mes(),
                                          Produto_Avaria.data_de_insercao <= ultimo_dia_mes()).order_by(
        Produto_Avaria.data_de_insercao.desc()).all()

    total_soma_avarias = db.session.query(func.sum(Produto_Avaria.preco_total)).filter(
        Produto_Avaria.data_de_insercao >= primeiro_dia_mes(),
        Produto_Avaria.data_de_insercao <= ultimo_dia_mes()).scalar()
    total_soma_avarias_usoeconsumo = db.session.query(func.sum(Produto_Avaria.preco_total)).filter(
        Produto_Avaria.data_de_insercao >= primeiro_dia_mes(), Produto_Avaria.data_de_insercao <= ultimo_dia_mes(),
        Produto_Avaria.usoeconsumo == "Sim").scalar()
    total_soma_avarias_embalagem = db.session.query(func.sum(Produto_Avaria.preco_total)).filter(
        Produto_Avaria.data_de_insercao >= primeiro_dia_mes(), Produto_Avaria.data_de_insercao <= ultimo_dia_mes(),
        Produto_Avaria.tipodeavaria == "Embalagem").scalar()
    total_soma_avarias_vencimento = db.session.query(func.sum(Produto_Avaria.preco_total)).filter(
        Produto_Avaria.data_de_insercao >= primeiro_dia_mes(), Produto_Avaria.data_de_insercao <= ultimo_dia_mes(),
        Produto_Avaria.tipodeavaria == "Vencido").scalar()
    total_soma_avarias_estragado = db.session.query(func.sum(Produto_Avaria.preco_total)).filter(
        Produto_Avaria.data_de_insercao >= primeiro_dia_mes(), Produto_Avaria.data_de_insercao <= ultimo_dia_mes(),
        Produto_Avaria.tipodeavaria == "Estragado").scalar()

    if not total_soma_avarias:
        total_soma_avarias = 0
    if not total_soma_avarias_usoeconsumo:
        total_soma_avarias_usoeconsumo = 0
    if not total_soma_avarias_embalagem:
        total_soma_avarias_embalagem = 0
    if not total_soma_avarias_vencimento:
        total_soma_avarias_vencimento = 0
    if not total_soma_avarias_estragado:
        total_soma_avarias_estragado = 0

    avarias_quantidade = db.session.query(func.sum(Produto_Avaria.quantidade)).filter(
        Produto_Avaria.data_de_insercao >= primeiro_dia_mes(),
        Produto_Avaria.data_de_insercao <= ultimo_dia_mes()).scalar()
    avarias_embalagem_quantidade = db.session.query(func.sum(Produto_Avaria.quantidade)).filter(
        Produto_Avaria.data_de_insercao >= primeiro_dia_mes(),
        Produto_Avaria.data_de_insercao <= ultimo_dia_mes(), Produto_Avaria.tipodeavaria == "Embalagem").scalar()
    avarias_vencidos_quantidade = db.session.query(func.sum(Produto_Avaria.quantidade)).filter(
        Produto_Avaria.data_de_insercao >= primeiro_dia_mes(),
        Produto_Avaria.data_de_insercao <= ultimo_dia_mes(), Produto_Avaria.tipodeavaria == "Vencido").scalar()
    avarias_estragados_quantidade = db.session.query(func.sum(Produto_Avaria.quantidade)).filter(
        Produto_Avaria.data_de_insercao >= primeiro_dia_mes(),
        Produto_Avaria.data_de_insercao <= ultimo_dia_mes(), Produto_Avaria.tipodeavaria == "Estragado").scalar()
    if not avarias_embalagem_quantidade:
        avarias_embalagem_quantidade = 0
    if not avarias_vencidos_quantidade:
        avarias_vencidos_quantidade = 0
    if not avarias_estragados_quantidade:
        avarias_estragados_quantidade = 0
    dez_itens = Produto_Avaria.query.filter(Produto_Avaria.data_de_insercao >= primeiro_dia_mes(),
                                            Produto_Avaria.data_de_insercao <= ultimo_dia_mes()).order_by(
        Produto_Avaria.preco_total.desc()).limit(10).all()
    return render_template('avarias/index.html', avarias=avarias, mes=mes_atual(),
                           total_soma_avarias=total_soma_avarias,
                           total_soma_avarias_usoeconsumo=total_soma_avarias_usoeconsumo,
                           total_soma_avarias_embalagem=total_soma_avarias_embalagem,
                           total_soma_avarias_vencimento=total_soma_avarias_vencimento,
                           total_soma_avarias_estragado=total_soma_avarias_estragado,
                           avarias_quantidade=avarias_quantidade,
                           avarias_embalagem_quantidade=avarias_embalagem_quantidade,
                           avarias_vencidos_quantidade=avarias_vencidos_quantidade,
                           avarias_estragados_quantidade=avarias_estragados_quantidade, dez_itens=dez_itens)


@app.route('/avarias/procurar')
@login_required
def avarias_procurar():
    return render_template('avarias/procurar.html')


@app.route('/avarias/cadastrar', methods=['POST'])
@login_required
def avarias_cadastrar():
    codigo = request.form['codigo']
    codigo_de_barras = request.form['codigo_barras']
    if codigo:
        produto = Produto.query.filter(Produto.codigo_do_produto == codigo).first()
        if produto:
            return render_template('avarias/cadastrar.html', produto=produto)
        else:
            return redirect(url_for('avarias_procurar'))
    if codigo_de_barras:
        produto = Produto.query.filter(Produto.codigo_de_barras == codigo_de_barras).first()
        if produto:
            return render_template('avarias/cadastrar.html', produto=produto)
        else:
            return redirect(url_for('avarias_procurar'))

    return render_template('avarias/cadastrar.html', data_agora=data_agora())


@app.route('/avarias/cadastro', methods=['POST'])
@login_required
def avarias_cadastro():
    codigo = request.form['codigo_produto']
    quantidade = Decimal(request.form['quantidade'])
    tipodeavaria = request.form['tipodeavaria']
    usoeconsumo = request.form['usoeconsumo']
    data_de_insercao = request.form['data_de_insercao']
    produto = Produto.query.filter(Produto.codigo_do_produto == codigo).first()
    cadastrar_avaria = Produto_Avaria(
        codigo_do_produto=produto.codigo_do_produto,
        nome_do_produto=produto.nome_do_produto,
        preco_do_produto=produto.preco_do_produto,
        quantidade=quantidade,
        preco_total=quantidade * Decimal(produto.preco_do_produto),
        data_de_insercao=data_de_insercao,
        criador=current_user.username,
        tipodeavaria=tipodeavaria,
        usoeconsumo=usoeconsumo)
    db.session.add(cadastrar_avaria)
    db.session.commit()
    db.session.close()
    return redirect("/avarias/")


@app.route('/avarias/relatorio', methods=['GET', 'POST'])
@login_required
def avarias_relatorio():
    if request.method == 'POST':
        codigo = request.form['codigo_produto']
        data_inicial = request.form['data_inicial']
        data_final = request.form['data_final']
        if codigo:
            resultado = Produto_Avaria.query.filter(Produto_Avaria.codigo_do_produto == codigo,
                                                    Produto_Avaria.data_de_insercao >= data_inicial,
                                                    Produto_Avaria.data_de_insercao <= data_final).order_by(
                Produto_Avaria.data_de_insercao.desc()).all()
            total_soma_avarias = db.session.query(func.sum(Produto_Avaria.preco_total)).filter(
                Produto_Avaria.codigo_do_produto == codigo,
                Produto_Avaria.data_de_insercao >= data_inicial,
                Produto_Avaria.data_de_insercao <= data_final).scalar()
            total_soma_avarias_usoeconsumo = db.session.query(func.sum(Produto_Avaria.preco_total)).filter(
                Produto_Avaria.codigo_do_produto == codigo,
                Produto_Avaria.data_de_insercao >= data_inicial,
                Produto_Avaria.data_de_insercao <= data_final, Produto_Avaria.usoeconsumo == "Sim").scalar()
            total_soma_avarias_embalagem = db.session.query(func.sum(Produto_Avaria.preco_total)).filter(
                Produto_Avaria.codigo_do_produto == codigo,
                Produto_Avaria.data_de_insercao >= data_inicial,
                Produto_Avaria.data_de_insercao <= data_final, Produto_Avaria.tipodeavaria == "Emalagem").scalar()
            total_soma_avarias_vencimento = db.session.query(func.sum(Produto_Avaria.preco_total)).filter(
                Produto_Avaria.codigo_do_produto == codigo,
                Produto_Avaria.data_de_insercao >= data_inicial,
                Produto_Avaria.data_de_insercao <= data_final, Produto_Avaria.tipodeavaria == "Vencido").scalar()
            total_soma_avarias_estragado = db.session.query(func.sum(Produto_Avaria.preco_total)).filter(
                Produto_Avaria.codigo_do_produto == codigo,
                Produto_Avaria.data_de_insercao >= data_inicial,
                Produto_Avaria.data_de_insercao <= data_final,
                Produto_Avaria.tipodeavaria == "Estragado").scalar()

            if not total_soma_avarias:
                total_soma_avarias = "0"
            if not total_soma_avarias_usoeconsumo:
                total_soma_avarias_usoeconsumo = "0"
            if not total_soma_avarias_embalagem:
                total_soma_avarias_embalagem = "0"
            if not total_soma_avarias_vencimento:
                total_soma_avarias_vencimento = "0"
            if not total_soma_avarias_estragado:
                total_soma_avarias_estragado = "0"

            avarias_quantidade = db.session.query(func.sum(Produto_Avaria.quantidade)).filter(
                Produto_Avaria.codigo_do_produto == codigo,
                Produto_Avaria.data_de_insercao >= data_inicial,
                Produto_Avaria.data_de_insercao <= data_final).scalar()
            avarias_embalagem_quantidade = db.session.query(func.sum(Produto_Avaria.quantidade)).filter(
                Produto_Avaria.codigo_do_produto == codigo,
                Produto_Avaria.data_de_insercao >= data_inicial,
                Produto_Avaria.data_de_insercao <= data_final, Produto_Avaria.tipodeavaria == "Embalagem").scalar()
            avarias_vencidos_quantidade = db.session.query(func.sum(Produto_Avaria.quantidade)).filter(
                Produto_Avaria.codigo_do_produto == codigo,
                Produto_Avaria.data_de_insercao >= data_inicial,
                Produto_Avaria.data_de_insercao <= data_final, Produto_Avaria.tipodeavaria == "Vencido").scalar()
            avarias_estragados_quantidade = db.session.query(func.sum(Produto_Avaria.quantidade)).filter(
                Produto_Avaria.codigo_do_produto == codigo,
                Produto_Avaria.data_de_insercao >= data_inicial,
                Produto_Avaria.data_de_insercao <= data_final, Produto_Avaria.tipodeavaria == "Estragado").scalar()
            if not avarias_embalagem_quantidade:
                avarias_embalagem_quantidade = 0
            if not avarias_vencidos_quantidade:
                avarias_vencidos_quantidade = 0
            if not avarias_estragados_quantidade:
                avarias_estragados_quantidade = 0

            dez_itens = Produto_Avaria.query.filter(Produto_Avaria.codigo_do_produto == codigo,
                                                    Produto_Avaria.data_de_insercao >= data_inicial,
                                                    Produto_Avaria.data_de_insercao <= data_final).order_by(
                Produto_Avaria.preco_total.desc()).limit(10).all()
            if total_soma_avarias == 0:
                redirect(url_for('/avarias/relatorio'))
            return render_template('avarias/emitir_relatorio.html', resultado=resultado,
                                   total_soma_avarias=total_soma_avarias,
                                   total_soma_avarias_usoeconsumo=total_soma_avarias_usoeconsumo,
                                   total_soma_avarias_embalagem=total_soma_avarias_embalagem,
                                   total_soma_avarias_vencimento=total_soma_avarias_vencimento,
                                   total_soma_avarias_estragado=total_soma_avarias_estragado,
                                   avarias_quantidade=avarias_quantidade,
                                   avarias_embalagem_quantidade=avarias_embalagem_quantidade,
                                   avarias_vencidos_quantidade=avarias_vencidos_quantidade,
                                   avarias_estragados_quantidade=avarias_estragados_quantidade,
                                   dez_itens=dez_itens, data_final=formatar_data(data_final),
                                   data_inicial=formatar_data(data_inicial))

        resultado = Produto_Avaria.query.filter(Produto_Avaria.data_de_insercao >= data_inicial,
                                                Produto_Avaria.data_de_insercao <= data_final).order_by(
            Produto_Avaria.data_de_insercao.desc()).all()
        total_soma_avarias = db.session.query(func.sum(Produto_Avaria.preco_total)).filter(
            Produto_Avaria.data_de_insercao >= data_inicial,
            Produto_Avaria.data_de_insercao <= data_final).scalar()
        total_soma_avarias = total_soma_avarias if total_soma_avarias is not None else 0
        total_soma_avarias_usoeconsumo = db.session.query(func.sum(Produto_Avaria.preco_total)).filter(
            Produto_Avaria.data_de_insercao >= data_inicial,
            Produto_Avaria.data_de_insercao <= data_final,
            Produto_Avaria.usoeconsumo == "Sim").scalar()
        total_soma_avarias_embalagem = db.session.query(func.sum(Produto_Avaria.preco_total)).filter(
            Produto_Avaria.data_de_insercao >= data_inicial,
            Produto_Avaria.data_de_insercao <= data_final,
            Produto_Avaria.tipodeavaria == "Embalagem").scalar()
        total_soma_avarias_vencimento = db.session.query(func.sum(Produto_Avaria.preco_total)).filter(
            Produto_Avaria.data_de_insercao >= data_inicial,
            Produto_Avaria.data_de_insercao <= data_final,
            Produto_Avaria.tipodeavaria == "Vencido").scalar()
        total_soma_avarias_estragado = db.session.query(func.sum(Produto_Avaria.preco_total)).filter(
            Produto_Avaria.data_de_insercao >= data_inicial,
            Produto_Avaria.data_de_insercao <= data_final,
            Produto_Avaria.tipodeavaria == "Estragado").scalar()

        if not total_soma_avarias:
            total_soma_avarias = 0
        if not total_soma_avarias_usoeconsumo:
            total_soma_avarias_usoeconsumo = 0
        if not total_soma_avarias_embalagem:
            total_soma_avarias_embalagem = 0
        if not total_soma_avarias_vencimento:
            total_soma_avarias_vencimento = 0
        if not total_soma_avarias_estragado:
            total_soma_avarias_estragado = 0

        avarias_quantidade = db.session.query(func.sum(Produto_Avaria.quantidade)).filter(
            Produto_Avaria.data_de_insercao >= data_inicial,
            Produto_Avaria.data_de_insercao <= data_final).scalar()
        avarias_embalagem_quantidade = db.session.query(func.sum(Produto_Avaria.quantidade)).filter(
            Produto_Avaria.data_de_insercao >= data_inicial,
            Produto_Avaria.data_de_insercao <= data_final, Produto_Avaria.tipodeavaria == "Embalagem").scalar()
        avarias_vencidos_quantidade = db.session.query(func.sum(Produto_Avaria.quantidade)).filter(
            Produto_Avaria.data_de_insercao >= data_inicial,
            Produto_Avaria.data_de_insercao <= data_final, Produto_Avaria.tipodeavaria == "Vencido").scalar()
        avarias_estragados_quantidade = db.session.query(func.sum(Produto_Avaria.quantidade)).filter(
            Produto_Avaria.data_de_insercao >= data_inicial,
            Produto_Avaria.data_de_insercao <= data_final, Produto_Avaria.tipodeavaria == "Estragado").scalar()
        if not avarias_embalagem_quantidade:
            avarias_embalagem_quantidade = 0
        if not avarias_vencidos_quantidade:
            avarias_vencidos_quantidade = 0
        if not avarias_estragados_quantidade:
            avarias_estragados_quantidade = 0

        dez_itens = Produto_Avaria.query.filter(Produto_Avaria.data_de_insercao >= data_inicial,
                                                Produto_Avaria.data_de_insercao <= data_final).order_by(
            Produto_Avaria.preco_total.desc()).limit(10).all()

        return render_template('avarias/emitir_relatorio.html', resultado=resultado,
                               total_soma_avarias=total_soma_avarias,
                               total_soma_avarias_usoeconsumo=total_soma_avarias_usoeconsumo,
                               total_soma_avarias_embalagem=total_soma_avarias_embalagem,
                               total_soma_avarias_vencimento=total_soma_avarias_vencimento,
                               total_soma_avarias_estragado=total_soma_avarias_estragado,
                               data_inicial=formatar_data(data_inicial), data_final=formatar_data(data_final),
                               avarias_quantidade=avarias_quantidade,
                               avarias_embalagem_quantidade=avarias_embalagem_quantidade,
                               avarias_vencidos_quantidade=avarias_vencidos_quantidade,
                               avarias_estragados_quantidade=avarias_estragados_quantidade,
                               dez_itens=dez_itens)
    return render_template('avarias/relatorio.html')


@app.route('/avarias/deletar/<int:avaria_id>', methods=["post", 'get'])
@login_required
def avarias_deletar(avaria_id):
    avaria_id = Produto_Avaria.query.get_or_404(avaria_id)
    db.session.delete(avaria_id)
    db.session.commit()
    return redirect(url_for('index_avarias'))


@app.route('/avarias/comparar', methods=['post', 'get'])
@login_required
def avarias_comparar():
    if request.method == 'POST':
        data_inicial1 = request.form['data_inicial1']
        data_final1 = request.form['data_final1']
        data_inicial2 = request.form['data_inicial2']
        data_final2 = request.form['data_final2']

        total_soma_avarias1 = db.session.query(func.sum(Produto_Avaria.preco_total)).filter(
            Produto_Avaria.data_de_insercao >= data_inicial1,
            Produto_Avaria.data_de_insercao <= data_final1).scalar()
        total_soma_avarias1 = total_soma_avarias1 if total_soma_avarias1 is not None else 0
        total_soma_avarias_usoeconsumo1 = db.session.query(func.sum(Produto_Avaria.preco_total)).filter(
            Produto_Avaria.data_de_insercao >= data_inicial1,
            Produto_Avaria.data_de_insercao <= data_final1,
            Produto_Avaria.usoeconsumo == "Sim").scalar()
        total_soma_avarias_embalagem1 = db.session.query(func.sum(Produto_Avaria.preco_total)).filter(
            Produto_Avaria.data_de_insercao >= data_inicial1,
            Produto_Avaria.data_de_insercao <= data_final1,
            Produto_Avaria.tipodeavaria == "Embalagem").scalar()
        total_soma_avarias_vencimento1 = db.session.query(func.sum(Produto_Avaria.preco_total)).filter(
            Produto_Avaria.data_de_insercao >= data_inicial1,
            Produto_Avaria.data_de_insercao <= data_final1,
            Produto_Avaria.tipodeavaria == "Vencido").scalar()
        total_soma_avarias_estragado1 = db.session.query(func.sum(Produto_Avaria.preco_total)).filter(
            Produto_Avaria.data_de_insercao >= data_inicial1,
            Produto_Avaria.data_de_insercao <= data_final1,
            Produto_Avaria.tipodeavaria == "Estragado").scalar()

        if not total_soma_avarias1:
            total_soma_avarias1 = 0
        if not total_soma_avarias_usoeconsumo1:
            total_soma_avarias_usoeconsumo1 = 0
        if not total_soma_avarias_embalagem1:
            total_soma_avarias_embalagem1 = 0
        if not total_soma_avarias_vencimento1:
            total_soma_avarias_vencimento1 = 0
        if not total_soma_avarias_estragado1:
            total_soma_avarias_estragado1 = 0

        total_soma_avarias2 = db.session.query(func.sum(Produto_Avaria.preco_total)).filter(
            Produto_Avaria.data_de_insercao >= data_inicial2,
            Produto_Avaria.data_de_insercao <= data_final2).scalar()
        total_soma_avarias2 = total_soma_avarias2 if total_soma_avarias2 is not None else 0
        total_soma_avarias_usoeconsumo2 = db.session.query(func.sum(Produto_Avaria.preco_total)).filter(
            Produto_Avaria.data_de_insercao >= data_inicial2,
            Produto_Avaria.data_de_insercao <= data_final2,
            Produto_Avaria.usoeconsumo == "Sim").scalar()
        total_soma_avarias_embalagem2 = db.session.query(func.sum(Produto_Avaria.preco_total)).filter(
            Produto_Avaria.data_de_insercao >= data_inicial2,
            Produto_Avaria.data_de_insercao <= data_final2,
            Produto_Avaria.tipodeavaria == "Embalagem").scalar()
        total_soma_avarias_vencimento2 = db.session.query(func.sum(Produto_Avaria.preco_total)).filter(
            Produto_Avaria.data_de_insercao >= data_inicial2,
            Produto_Avaria.data_de_insercao <= data_final2,
            Produto_Avaria.tipodeavaria == "Vencido").scalar()
        total_soma_avarias_estragado2 = db.session.query(func.sum(Produto_Avaria.preco_total)).filter(
            Produto_Avaria.data_de_insercao >= data_inicial2,
            Produto_Avaria.data_de_insercao <= data_final2,
            Produto_Avaria.tipodeavaria == "Estragado").scalar()

        if not total_soma_avarias2:
            total_soma_avarias2 = 0
        if not total_soma_avarias_usoeconsumo2:
            total_soma_avarias_usoeconsumo2 = 0
        if not total_soma_avarias_embalagem2:
            total_soma_avarias_embalagem2 = 0
        if not total_soma_avarias_vencimento2:
            total_soma_avarias_vencimento2 = 0
        if not total_soma_avarias_estragado2:
            total_soma_avarias_estragado2 = 0

        avarias_quantidade1 = db.session.query(func.sum(Produto_Avaria.quantidade)).filter(
            Produto_Avaria.data_de_insercao >= data_inicial1,
            Produto_Avaria.data_de_insercao <= data_final1).scalar()
        avarias_embalagem_quantidade1 = db.session.query(func.sum(Produto_Avaria.quantidade)).filter(
            Produto_Avaria.data_de_insercao >= data_inicial1,
            Produto_Avaria.data_de_insercao <= data_final1, Produto_Avaria.tipodeavaria == "Embalagem").scalar()
        avarias_vencidos_quantidade1 = db.session.query(func.sum(Produto_Avaria.quantidade)).filter(
            Produto_Avaria.data_de_insercao >= data_inicial1,
            Produto_Avaria.data_de_insercao <= data_final1, Produto_Avaria.tipodeavaria == "Vencido").scalar()
        avarias_estragados_quantidade1 = db.session.query(func.sum(Produto_Avaria.quantidade)).filter(
            Produto_Avaria.data_de_insercao >= data_inicial1,
            Produto_Avaria.data_de_insercao <= data_final1, Produto_Avaria.tipodeavaria == "Estragado").scalar()
        if not avarias_embalagem_quantidade1:
            avarias_embalagem_quantidade1 = 0
        if not avarias_vencidos_quantidade1:
            avarias_vencidos_quantidade1 = 0
        if not avarias_estragados_quantidade1:
            avarias_estragados_quantidade1 = 0

        avarias_quantidade2 = db.session.query(func.sum(Produto_Avaria.quantidade)).filter(
            Produto_Avaria.data_de_insercao >= data_inicial2,
            Produto_Avaria.data_de_insercao <= data_final2).scalar()
        avarias_embalagem_quantidade2 = db.session.query(func.sum(Produto_Avaria.quantidade)).filter(
            Produto_Avaria.data_de_insercao >= data_inicial2,
            Produto_Avaria.data_de_insercao <= data_final2, Produto_Avaria.tipodeavaria == "Embalagem").scalar()
        avarias_vencidos_quantidade2 = db.session.query(func.sum(Produto_Avaria.quantidade)).filter(
            Produto_Avaria.data_de_insercao >= data_inicial2,
            Produto_Avaria.data_de_insercao <= data_final2, Produto_Avaria.tipodeavaria == "Vencido").scalar()
        avarias_estragados_quantidade2 = db.session.query(func.sum(Produto_Avaria.quantidade)).filter(
            Produto_Avaria.data_de_insercao >= data_inicial2,
            Produto_Avaria.data_de_insercao <= data_final2, Produto_Avaria.tipodeavaria == "Estragado").scalar()
        if not avarias_embalagem_quantidade2:
            avarias_embalagem_quantidade2 = 0
        if not avarias_vencidos_quantidade2:
            avarias_vencidos_quantidade2 = 0
        if not avarias_estragados_quantidade2:
            avarias_estragados_quantidade2 = 0
        array_total=[]
        array_total.append(total_soma_avarias1)
        array_total.append(total_soma_avarias2)
        return render_template('avarias/comparar.html',
                               total_soma_avarias1=total_soma_avarias1, array_total=array_total,
                               total_soma_avarias_usoeconsumo1=total_soma_avarias_usoeconsumo1,
                               total_soma_avarias_embalagem1=total_soma_avarias_embalagem1,
                               total_soma_avarias_vencimento1=total_soma_avarias_vencimento1,
                               total_soma_avarias_estragado1=total_soma_avarias_estragado1,
                               data_inicial1=formatar_data(data_inicial1), data_final1=formatar_data(data_final1),
                               avarias_quantidade1=avarias_quantidade1,
                               avarias_embalagem_quantidade1=avarias_embalagem_quantidade1,
                               avarias_vencidos_quantidade1=avarias_vencidos_quantidade1,
                               avarias_estragados_quantidade1=avarias_estragados_quantidade1,
                               total_soma_avarias2=total_soma_avarias2,
                               total_soma_avarias_usoeconsumo2=total_soma_avarias_usoeconsumo2,
                               total_soma_avarias_embalagem2=total_soma_avarias_embalagem2,
                               total_soma_avarias_vencimento2=total_soma_avarias_vencimento2,
                               total_soma_avarias_estragado2=total_soma_avarias_estragado2,
                               data_inicial2=formatar_data(data_inicial2), data_final2=formatar_data(data_final2),
                               avarias_quantidade2=avarias_quantidade2,
                               avarias_embalagem_quantidade2=avarias_embalagem_quantidade2,
                               avarias_vencidos_quantidade2=avarias_vencidos_quantidade2,
                               avarias_estragados_quantidade2=avarias_estragados_quantidade2, calcular_porcentagem=calcular_porcentagem)
    return render_template('avarias/comparar.html')


#FIM AVARIAS

