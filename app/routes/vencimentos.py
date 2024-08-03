from ..main import *
@app.route('/vencimentos/', methods=['GET'])
def index_vencimentos():
    vencimentos = Produto_Vencimento.query.order_by(Produto_Vencimento.data_de_vencimento.asc()).all()
    for vencimento in vencimentos:
        diferenca = vencimento.data_de_vencimento - datetime.now().date()
        vencimento.dias_restantes = diferenca.days
    return render_template('vencimentos/index.html', vencimentos=vencimentos, data_agora=data_agora())

@app.route('/vencimentos/procurar')
@login_required
def vencimentos_procurar():
    return render_template('vencimentos/procurar.html')


@app.route('/vencimentos/cadastrar', methods=['POST'])
@login_required
def vencimentos_cadastrar():
    codigo = request.form['codigo']
    codigo_de_barras = request.form['codigo_barras']
    if codigo:
        produto = Produto.query.filter(Produto.codigo_do_produto == codigo).first()
        return render_template('vencimentos/cadastrar.html', produto=produto)
    if codigo_de_barras:
        produto = Produto.query.filter(Produto.codigo_de_barras == codigo_de_barras).first()
        return render_template('vencimentos/cadastrar.html', produto=produto)

    return render_template('vencimentos/cadastrar.html')


@app.route('/vencimentos/cadastro', methods=['POST'])
@login_required
def vencimentos_cadastro():
    codigo = request.form['codigo_produto']
    quantidade = Decimal(request.form['quantidade'])
    data_de_vencimento = request.form['data_vencimento']
    produto = Produto.query.filter(Produto.codigo_do_produto == codigo).first()
    cadastrar_vencimentos = Produto_Vencimento(
        codigo_do_produto=produto.codigo_do_produto,
        nome_do_produto=produto.nome_do_produto,
        quantidade=quantidade,
        data_de_vencimento=formatar_data(data_de_vencimento),
        data_de_insercao=data_agora(),
        criador=current_user.username)
    db.session.add(cadastrar_vencimentos)
    db.session.commit()
    db.session.close()
    return redirect("/vencimentos/")


@app.route('/vencimentos/editar/<int:vencimento_id>', methods=('GET', 'POST'))
@login_required
def produto_vencimento_editar(vencimento_id):
    vencimento = Produto_Vencimento.query.get_or_404(vencimento_id)

    if request.method == 'POST':
        quantidade = request.form['quantidade']
        vencimento.quantidade = quantidade
        db.session.add(vencimento)
        db.session.commit()
        return redirect(url_for('index_vencimentos'))

    return render_template('/vencimentos/editar.html', vencimento=vencimento)


@app.route('/vencimentos/deletar/<int:vencimento_id>', methods=["post"])
@login_required
def vencimento_deletar(vencimento_id):
    vencimento_id = Produto_Vencimento.query.get_or_404(vencimento_id)
    db.session.delete(vencimento_id)
    db.session.commit()
    return redirect(url_for('index_vencimentos'))


@app.route('/vencimentos/cadastrar_volume', methods=['GET', 'POST'])
@login_required
def cadastrar_volume():
    if request.method == 'POST':
        codigo_do_produto = request.form['codigo_produto']
        mediames = request.form['media_saida']
        if Produto.query.filter(Volume_de_Vendas.codigo_do_produto == codigo_do_produto).first():
            db.session.query(Volume_de_Vendas).filter(Volume_de_Vendas.codigo_do_produto == codigo_do_produto).update(
                {Volume_de_Vendas.mediames: mediames})
            db.session.commit()
            return render_template("/vencimentos/cadastrar_volume.html")
        volume = Volume_de_Vendas(codigo_do_produto=codigo_do_produto, mediames=mediames)
        db.session.add(volume)
        db.session.commit()
    return render_template("/vencimentos/cadastrar_volume.html")


@app.route("/vencimentos/analisarvolume", methods=["GET"])
@login_required
def analisarvolume():
    resultados = db.session.query(
        Produto_Vencimento.codigo_do_produto,
        Produto_Vencimento.quantidade,
        Produto_Vencimento.nome_do_produto,
        Produto_Vencimento.quantidade,
        Produto_Vencimento.data_de_vencimento,
        Volume_de_Vendas.mediames
    ).join(Volume_de_Vendas, Produto_Vencimento.codigo_do_produto == Volume_de_Vendas.codigo_do_produto).all()
    dados = []
    for resultado in resultados:
        diferenca = resultado.data_de_vencimento - datetime.now().date()
        dias_restantes = diferenca.days
        if resultado.mediames == 0:
            media_diaria = 0
        else:
            media_diaria = resultado.mediames / 30  # Calculando a média diária

        dados.append({
            'codigo_do_produto': resultado.codigo_do_produto,
            'nome_do_produto': resultado.nome_do_produto,
            'quantidade': float(resultado.quantidade),
            'data_de_vencimento': resultado.data_de_vencimento.isoformat(),  # Convertendo para string
            'dias_restantes': int(dias_restantes),
            'media_mensal': int(resultado.mediames),
            'media_diaria': float(media_diaria),
        })

    return render_template("/vencimentos/analisarvolume.html", dados=dados)

