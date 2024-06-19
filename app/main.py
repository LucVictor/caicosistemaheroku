import os
from flask import Flask, render_template, request, url_for, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
import locale
import calendar
from datetime import datetime
from sqlalchemy import func
from decimal import Decimal
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from babel.dates import format_date, format_datetime, format_time
from datetime import datetime

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bancodedados.db"
app.config["SECRET_KEY"] = "secretkey"
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo_do_produto = db.Column(db.Integer, nullable=False)
    nome_do_produto = db.Column(db.String(300), nullable=False)
    preco_do_produto = db.Column(db.DECIMAL(10, 2), nullable=False)
    codigo_de_barras = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<{self.nome_do_produto}>'


class Produto_Vencimento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo_do_produto = db.Column(db.Integer, nullable=False)
    nome_do_produto = db.Column(db.String(300), nullable=False)
    quantidade = db.Column(db.DECIMAL(10, 2), nullable=False)
    data_de_vencimento = db.Column(db.Date)
    data_de_insercao = db.Column(db.Date)
    criador = db.Column(db.String(300), nullable=True)


class Produto_Avaria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo_do_produto = db.Column(db.Integer, nullable=False)
    nome_do_produto = db.Column(db.String(300), nullable=False)
    preco_do_produto = db.Column(db.DECIMAL(10, 2), nullable=False)
    quantidade = db.Column(db.DECIMAL(10, 2), nullable=False)
    preco_total = db.Column(db.DECIMAL(10, 2), nullable=False)
    data_de_vencimento = db.Column(db.Date)
    data_de_insercao = db.Column(db.Date)
    criador = db.Column(db.String(300), nullable=True)
    tipodeavaria = db.Column(db.String(300), nullable=True)
    cozinha = db.Column(db.String(300), nullable=True)

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    filial = db.Column(db.String(250), nullable=True)

class Volume_de_Vendas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo_do_produto = db.Column(db.Integer, nullable=False)
    mediames = db.Column(db.DECIMAL, nullable=False)


@login_manager.user_loader
def loader_user(user_id):
    return Users.query.get(user_id)

@app.template_filter('round_quantity')
def round_quantity_filter(value):
    a = round(value)
    return int(a)

criador = current_user

@app.template_filter('format_quantidade')
def format_quantidade(value):
    if isinstance(value, Decimal) and value == value.to_integral_value():
        return int(value)
    return value
@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/logar')
def formatar_data(x):
    x = datetime.strptime(x, '%Y-%m-%d').date()
    return x


def data_agora():
    agora = datetime.now().date()
    return agora

def mes_atual():
    mes = datetime.now()
    formatted_date = format_datetime(mes, format='MMMM', locale='pt_BR')
    return formatted_date

def primeiro_dia_mes():
    primeiro_dia_mes = data_agora().replace(day=1)
    return primeiro_dia_mes
def ultimo_dia_mes():
    ultimo_dia_mes = data_agora().replace(day=calendar.monthrange(data_agora().year, data_agora().month)[1])
    return ultimo_dia_mes

@app.route('/')
def index():
        db.create_all()
        start_date = primeiro_dia_mes()
        end_date = ultimo_dia_mes()

        query = db.session.query(
            Produto_Avaria.data_de_insercao,
            func.sum(Produto_Avaria.preco_total).label('total_value')
        )

        if start_date:
            query = query.filter(Produto_Avaria.data_de_insercao >= start_date)

        if end_date:
            query = query.filter(Produto_Avaria.data_de_insercao <= end_date)

        results = query.group_by(Produto_Avaria.data_de_insercao).all()

        dates = [result.data_de_insercao.strftime('%d-%m') for result in results]
        total_values = [result.total_value for result in results]
        print(dates)
        print(total_values)
        return render_template('index.html', dates=dates, total_values=total_values)


#AVARIAS


@app.route('/avarias/', methods=['GET'])
def index_avarias():
    avarias = Produto_Avaria.query.filter(Produto_Avaria.data_de_insercao >= primeiro_dia_mes(), Produto_Avaria.data_de_insercao <= ultimo_dia_mes()).order_by(
        Produto_Avaria.data_de_insercao.desc()).all()

    total_soma_avarias = db.session.query(func.sum(Produto_Avaria.preco_total)).filter(Produto_Avaria.data_de_insercao >= primeiro_dia_mes(), Produto_Avaria.data_de_insercao <= ultimo_dia_mes()).scalar()
    return render_template('avarias/index.html', avarias=avarias, mes=mes_atual(), total_soma_avarias=total_soma_avarias)


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
        return render_template('avarias/cadastrar.html', produto=produto)
    if codigo_de_barras:
        produto = Produto.query.filter(Produto.codigo_de_barras == codigo_de_barras).first()
        return render_template('avarias/cadastrar.html', produto=produto)

    return render_template('avarias/cadastrar.html')


@app.route('/avarias/cadastro', methods=['POST'])
@login_required
def avarias_cadastro():
    codigo = request.form['codigo_produto']
    quantidade = int(request.form['quantidade'])
    data_de_vencimento = request.form['data_vencimento']
    tipodeavaria = request.form['tipodeavaria']
    cozinha = request.form['cozinha']
    produto = Produto.query.filter(Produto.codigo_do_produto == codigo).first()
    cadastrar_avaria = Produto_Avaria(
        codigo_do_produto=produto.codigo_do_produto,
        nome_do_produto=produto.nome_do_produto,
        preco_do_produto=produto.preco_do_produto,
        quantidade=quantidade,
        preco_total=quantidade * produto.preco_do_produto,
        data_de_vencimento=formatar_data(data_de_vencimento),
        data_de_insercao=data_agora(),
        criador=current_user.username,
        tipodeavaria=tipodeavaria,
        cozinha=cozinha)
    db.session.add(cadastrar_avaria)
    db.session.commit()
    db.session.close()
    return url_for("avarias_cadastrar")

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
                                                    Produto_Avaria.data_de_insercao <= data_final).order_by(Produto_Avaria.data_de_insercao.desc()).all()
            total_soma_avarias = db.session.query(func.sum(resultado.preco_total)).filter(Produto_Avaria.codigo_do_produto == codigo,
                                                    Produto_Avaria.data_de_insercao >= data_inicial,
                                                    Produto_Avaria.data_de_insercao <= data_final).scalar()
            total_soma_avarias = total_soma_avarias if total_soma_avarias is not None else 0
            return render_template('avarias/emitir_relatorio.html', resultado=resultado, total_soma_avarias= total_soma_avarias)

        resultado = Produto_Avaria.query.filter(Produto_Avaria.data_de_insercao >= data_inicial,
                                                Produto_Avaria.data_de_insercao <= data_final).order_by(Produto_Avaria.data_de_insercao.desc()).all()
        total_soma_avarias = db.session.query(func.sum(Produto_Avaria.preco_total)).filter(Produto_Avaria.data_de_insercao >= data_inicial,
                                                Produto_Avaria.data_de_insercao <= data_final).scalar()
        total_soma_avarias = total_soma_avarias if total_soma_avarias is not None else 0
        return render_template('avarias/emitir_relatorio.html', resultado=resultado,
                               total_soma_avarias=total_soma_avarias)
    return render_template('avarias/relatorio.html')


@app.route('/avarias/deletar/<int:avaria_id>', methods=["post", 'get'])
@login_required
def avarias_deletar(avaria_id):
    avaria_id = Produto_Avaria.query.get_or_404(avaria_id)
    db.session.delete(avaria_id)
    db.session.commit()
    return redirect(url_for('index_avarias'))

#FIM AVARIAS




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

    return render_template('avarias/cadastrar.html')


@app.route('/vencimentos/cadastro', methods=['POST'])
@login_required
def vencimentos_cadastro():
    codigo = request.form['codigo_produto']
    quantidade = int(request.form['quantidade'])
    data_de_vencimento = request.form['data_vencimento']
    produto = Produto.query.filter(Produto.codigo_do_produto == codigo).first()
    cadastrar_vencimentos = Produto_Vencimento(
        codigo_do_produto=produto.codigo_do_produto,
        nome_do_produto=produto.nome_do_produto,
        quantidade=quantidade,
        data_de_vencimento=formatar_data(data_de_vencimento),
        data_de_insercao=data_agora(),
        criador = current_user.username)
    db.session.add(cadastrar_vencimentos)
    db.session.commit()
    db.session.close()
    return url_for("index_vencimentos")




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


@app.route('/cadastrar', methods=["GET", "POST"])
@login_required
def cadastrar():
    if request.method == "POST":
        user = Users(username=request.form.get("username"),
                     password=request.form.get("password"), filial=request.form.get("filial"))
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("logar"))
    return render_template("registrar.html")


@app.route("/logar", methods=["GET", "POST"])
def logar():
    if request.method == "POST":
        user = Users.query.filter_by(
            username=request.form.get("username")).first()
        if user.password == request.form.get("password"):
            login_user(user)
            return redirect(url_for("index"))
    return render_template("logar.html")

@app.route("/sair")
def sair():
    logout_user()
    return redirect(url_for("logar"))

@app.route("/vencimentos/analisarvolume", methods=["GET"])
def anlisarvolume():
    resultados = db.session.query(
        Produto_Vencimento.codigo_do_produto,
        Produto_Vencimento.quantidade,
        Produto_Vencimento.nome_do_produto,
        Produto_Vencimento.quantidade,
        Produto_Vencimento.data_de_vencimento,
        Volume_de_Vendas.mediames
    ).join(Volume_de_Vendas, Produto_Vencimento.codigo_do_produto == Volume_de_Vendas.codigo_do_produto).all()
    dados=[]
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
