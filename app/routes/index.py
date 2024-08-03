from ..main import *
@app.route('/')
@login_required
def index():
    start_date = primeiro_dia_mes()
    end_date = ultimo_dia_mes()

    avarias = db.session.query(
        Produto_Avaria.data_de_insercao,
        func.sum(Produto_Avaria.preco_total).label('total_value')
    )

    if start_date:
        avarias = avarias.filter(Produto_Avaria.data_de_insercao >= start_date)

    if end_date:
        avarias = avarias.filter(Produto_Avaria.data_de_insercao <= end_date)

    results = avarias.group_by(Produto_Avaria.data_de_insercao).all()
    dates = [result.data_de_insercao.strftime('%d-%m') for result in results]
    total_values = [result.total_value for result in results]
    dez_itens = Produto_Avaria.query.order_by(
        Produto_Avaria.data_de_insercao.desc()).limit(5).all()
    dez_vencimentos = Produto_Vencimento.query.order_by(
        Produto_Vencimento.data_de_vencimento).limit(5).all()
    return render_template('index.html', dates=dates, total_values=total_values, dez_itens=dez_itens,
                           dez_vencimentos=dez_vencimentos)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('download_file', name=filename))
    return render_template("upload.html")


