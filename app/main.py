import os

import sqlalchemy
from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import calendar
from sqlalchemy import func, case, cast, Time
from decimal import Decimal
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from babel.dates import format_datetime
from datetime import datetime, timedelta, time
from functools import wraps

UPLOAD_FOLDER = "app/static/uploads"
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://lucascod_banco:88335938@192.95.54.248/lucascod_banco"
app.config["SECRET_KEY"] = "secretkey"
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_recycle': 28000,
    'pool_pre_ping': True
}
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo_do_produto = db.Column(db.Integer, nullable=False)
    nome_do_produto = db.Column(db.String(300), nullable=False)
    preco_do_produto = db.Column(db.DECIMAL(10, 2), nullable=False)
    codigo_de_barras = db.Column(db.String(300), nullable=False)

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
    data_de_insercao = db.Column(db.Date)
    criador = db.Column(db.String(300), nullable=True)
    tipodeavaria = db.Column(db.String(300), nullable=True)
    cozinha = db.Column(db.String(300), nullable=True)


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    filial = db.Column(db.String(250), nullable=True)
    acesso = db.Column(db.String(250), nullable=False)


class Volume_de_Vendas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo_do_produto = db.Column(db.Integer, nullable=False)
    mediames = db.Column(db.DECIMAL, nullable=False)


class Entrega(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_da_entrega = db.Column(db.Date, nullable=False)
    motorista = db.Column(db.String(250), nullable=False)
    ajudante = db.Column(db.String(250), nullable=False)
    rota = db.Column(db.String(250), nullable=False)
    quantidade_de_entregas = db.Column(db.Integer, nullable=False)
    tempo_total = db.Column(db.Time, nullable=False)
    tempo_total_entrega = db.Column(db.Time, nullable=False)
    tempo_medio_total = db.Column(db.Time, nullable=False)
    tempo_medio_entrega = db.Column(db.Time, nullable=False)
    resultado_tempo = db.Column(db.String(250), nullable=False)
    reentregas = db.Column(db.Integer, nullable=True)


class Rotas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rota = db.Column(db.String(250), unique=True, nullable=False)
    tempo_medio_rota = db.Column(db.Time, nullable=False)


class Funcionarios(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(250), unique=True, nullable=False)
    funcao = db.Column(db.String(250), nullable=False)


class Erros(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_do_erro = db.Column(db.Date, nullable=False)
    erro_funcionario = db.Column(db.String(250), nullable=False)
    erro_cliente = db.Column(db.String(250), nullable=False)
    quantidade_de_erros = db.Column(db.Integer, nullable=False)
    motorista_da_entrega = db.Column(db.String(250), nullable=False)
    produto_erro = db.Column(db.String(250), nullable=False)
    descricao_do_erro = db.Column(db.String(1000), nullable=True)

    @classmethod
    def motorista(cls, nome):
        return cls(nome=nome, funcao='Motorista')

    @classmethod
    def ajudante(cls, nome):
        return cls(nome=nome, funcao='Ajudante')

    @classmethod
    def vendedor(cls, nome):
        return cls(nome=nome, funcao='Vendedor')

    @classmethod
    def conferente(cls, nome):
        return cls(nome=nome, funcao='Conferente')

    @classmethod
    def faturista(cls, nome):
        return cls(nome=nome, funcao='Faturista')


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


def access_level_required(level):
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if current_user.acesso < level:
                return redirect(url_for('index'))
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def hora_para_segundo(t):
    return t.hour * 3600 + t.minute * 60 + t.second


def segundos_para_hora(seconds):
    return (datetime.min + timedelta(seconds=seconds)).time()


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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


def recalcular_rotas(rotax):
    sum_tempo_medio_entrega = db.session.query(
        Entrega.rota,
        func.sum(
            (func.hour(Entrega.tempo_medio_entrega) * 3600) +
            (func.minute(Entrega.tempo_medio_entrega) * 60) +
            func.second(Entrega.tempo_medio_entrega)
        ).label('sum_tempo_medio_entrega'),
        func.count(Entrega.id).label('total_entregas')
    ).filter(
        Entrega.rota == rotax
    ).group_by(
        Entrega.rota
    ).all()
    for sum_tempo in sum_tempo_medio_entrega:
        rota = Rotas.query.filter_by(rota=sum_tempo.rota).first()
        if rota and sum_tempo.total_entregas > 0:
            total_seconds = int(sum_tempo.sum_tempo_medio_entrega / sum_tempo.total_entregas)
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            rota.tempo_medio_rota = time(hours, minutes, seconds)
            db.session.commit()


@app.route('/')
@login_required
def index():
    db.create_all()
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
        Produto_Vencimento.data_de_vencimento.desc()).limit(5).all()
    return render_template('index.html', dates=dates, total_values=total_values, dez_itens=dez_itens,
                           dez_vencimentos=dez_vencimentos)


#AVARIAS


@app.route('/avarias/', methods=['GET'])
@login_required
def index_avarias():
    avarias = Produto_Avaria.query.filter(Produto_Avaria.data_de_insercao >= primeiro_dia_mes(),
                                          Produto_Avaria.data_de_insercao <= ultimo_dia_mes()).order_by(
        Produto_Avaria.data_de_insercao.desc()).all()

    total_soma_avarias = db.session.query(func.sum(Produto_Avaria.preco_total)).filter(
        Produto_Avaria.data_de_insercao >= primeiro_dia_mes(),
        Produto_Avaria.data_de_insercao <= ultimo_dia_mes()).scalar()
    total_soma_avarias_cozinha = db.session.query(func.sum(Produto_Avaria.preco_total)).filter(
        Produto_Avaria.data_de_insercao >= primeiro_dia_mes(), Produto_Avaria.data_de_insercao <= ultimo_dia_mes(),
        Produto_Avaria.cozinha == "Sim").scalar()
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
    if not total_soma_avarias_cozinha:
        total_soma_avarias_cozinha = 0
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
                           total_soma_avarias=total_soma_avarias, total_soma_avarias_cozinha=total_soma_avarias_cozinha,
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
    tipodeavaria = request.form['tipodeavaria']
    cozinha = request.form['cozinha']
    produto = Produto.query.filter(Produto.codigo_do_produto == codigo).first()
    cadastrar_avaria = Produto_Avaria(
        codigo_do_produto=produto.codigo_do_produto,
        nome_do_produto=produto.nome_do_produto,
        preco_do_produto=produto.preco_do_produto,
        quantidade=quantidade,
        preco_total=quantidade * produto.preco_do_produto,
        data_de_insercao=data_agora(),
        criador=current_user.username,
        tipodeavaria=tipodeavaria,
        cozinha=cozinha)
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
            total_soma_avarias_cozinha = db.session.query(func.sum(Produto_Avaria.preco_total)).filter(
                Produto_Avaria.codigo_do_produto == codigo,
                Produto_Avaria.data_de_insercao >= data_inicial,
                Produto_Avaria.data_de_insercao <= data_final, Produto_Avaria.cozinha == "Sim").scalar()
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
            if not total_soma_avarias_cozinha:
                total_soma_avarias_cozinha = "0"
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
                avarias_embalagem_quantidade = "0"
            if not avarias_vencidos_quantidade:
                avarias_vencidos_quantidade = "0"
            if not avarias_estragados_quantidade:
                avarias_estragados_quantidade = "0"

            dez_itens = Produto_Avaria.query.filter(Produto_Avaria.codigo_do_produto == codigo,
                                                    Produto_Avaria.data_de_insercao >= data_inicial,
                                                    Produto_Avaria.data_de_insercao <= data_final).order_by(
                Produto_Avaria.preco_total.desc()).limit(10).all()

            return render_template('avarias/emitir_relatorio.html', resultado=resultado,
                                   total_soma_avarias=total_soma_avarias,
                                   total_soma_avarias_cozinha=total_soma_avarias_cozinha,
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
        total_soma_avarias_cozinha = db.session.query(func.sum(Produto_Avaria.preco_total)).filter(
            Produto_Avaria.data_de_insercao >= data_inicial,
            Produto_Avaria.data_de_insercao <= data_final,
            Produto_Avaria.cozinha == "Sim").scalar()
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
            total_soma_avarias = "0.00"
        if not total_soma_avarias_cozinha:
            total_soma_avarias_cozinha = "0.00"
        if not total_soma_avarias_embalagem:
            total_soma_avarias_embalagem = "0.00"
        if not total_soma_avarias_vencimento:
            total_soma_avarias_vencimento = "0.00"
        if not total_soma_avarias_estragado:
            total_soma_avarias_estragado = "0.00"

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
            avarias_embalagem_quantidade = "0"
        if not avarias_vencidos_quantidade:
            avarias_vencidos_quantidade = "0"
        if not avarias_estragados_quantidade:
            avarias_estragados_quantidade = "0"

        dez_itens = Produto_Avaria.query.filter(Produto_Avaria.data_de_insercao >= data_inicial,
                                                Produto_Avaria.data_de_insercao <= data_final).order_by(
            Produto_Avaria.preco_total.desc()).limit(10).all()

        return render_template('avarias/emitir_relatorio.html', resultado=resultado,
                               total_soma_avarias=total_soma_avarias,
                               total_soma_avarias_cozinha=total_soma_avarias_cozinha,
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
        total_soma_avarias_cozinha1 = db.session.query(func.sum(Produto_Avaria.preco_total)).filter(
            Produto_Avaria.data_de_insercao >= data_inicial1,
            Produto_Avaria.data_de_insercao <= data_final1,
            Produto_Avaria.cozinha == "Sim").scalar()
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
        if not total_soma_avarias_cozinha1:
            total_soma_avarias_cozinha1 = 0
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
        total_soma_avarias_cozinha2 = db.session.query(func.sum(Produto_Avaria.preco_total)).filter(
            Produto_Avaria.data_de_insercao >= data_inicial2,
            Produto_Avaria.data_de_insercao <= data_final2,
            Produto_Avaria.cozinha == "Sim").scalar()
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
        if not total_soma_avarias_cozinha2:
            total_soma_avarias_cozinha2 = 0
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

        return render_template('avarias/comparar.html',
                               total_soma_avarias1=total_soma_avarias1,
                               total_soma_avarias_cozinha1=total_soma_avarias_cozinha1,
                               total_soma_avarias_embalagem1=total_soma_avarias_embalagem1,
                               total_soma_avarias_vencimento1=total_soma_avarias_vencimento1,
                               total_soma_avarias_estragado1=total_soma_avarias_estragado1,
                               data_inicial1=formatar_data(data_inicial1), data_final1=formatar_data(data_final1),
                               avarias_quantidade1=avarias_quantidade1,
                               avarias_embalagem_quantidade1=avarias_embalagem_quantidade1,
                               avarias_vencidos_quantidade1=avarias_vencidos_quantidade1,
                               avarias_estragados_quantidade1=avarias_estragados_quantidade1,
                               total_soma_avarias2=total_soma_avarias2,
                               total_soma_avarias_cozinha2=total_soma_avarias_cozinha2,
                               total_soma_avarias_embalagem2=total_soma_avarias_embalagem2,
                               total_soma_avarias_vencimento2=total_soma_avarias_vencimento2,
                               total_soma_avarias_estragado2=total_soma_avarias_estragado2,
                               data_inicial2=formatar_data(data_inicial2), data_final2=formatar_data(data_final2),
                               avarias_quantidade2=avarias_quantidade2,
                               avarias_embalagem_quantidade2=avarias_embalagem_quantidade2,
                               avarias_vencidos_quantidade2=avarias_vencidos_quantidade2,
                               avarias_estragados_quantidade2=avarias_estragados_quantidade2)
    return render_template('avarias/comparar.html')


#FIM AVARIAS


@app.route('/vencimentos/', methods=['GET'])
@login_required
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
        criador=current_user.username)
    db.session.add(cadastrar_vencimentos)
    db.session.commit()
    db.session.close()
    return redirect("/avarias/")


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
    total_sum = total_positivo + total_negativo
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
    return render_template('entregas/index.html', total_de_reentregas=total_de_reentregas,
                           total_de_entregas=total_de_entregas, mes=mes, rotas=rotas, entregas=entregas,
                           data_agora=data_agora(),
                           resultados=resultados, resultados_entregas=resultados_entregas)


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
    total_sum = total_positivo + total_negativo
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
    return render_template('entregas/emitir_relatorio.html', total_de_reentregas=total_de_reentregas,
                           total_de_entregas=total_de_entregas, mes=mes,
                           entregas=entregas, data_agora=data_agora(), resultados=resultados,
                           resultados_entregas=resultados_entregas, data_inicial=formatar_data(data_inicial),
                           data_final=formatar_data(data_final))


@app.route('/entregas/cadastrar', methods=['GET', 'POST'])
@login_required
@access_level_required(1)
def entrega_cadastrar():
    if request.method == 'POST':
        data_da_entrega = datetime.strptime(request.form['data_da_entrega'], '%Y-%m-%d').date()
        motorista = request.form['motorista']
        ajudante = request.form['ajudante']
        rota = request.form['rota']
        quantidade_de_entregas = int(request.form['quantidade_de_entregas'])
        tempo_total = datetime.strptime(request.form['tempo_total'], '%H:%M').time()
        reentregas = int(request.form['reentregas'])
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
            rota=rota,
            quantidade_de_entregas=quantidade_de_entregas,
            tempo_total=tempo_total,
            tempo_total_entrega=tempo_total_entrega,
            tempo_medio_total=tempo_medio_total,
            tempo_medio_entrega=tempo_medio_entrega,
            resultado_tempo=resultado_tempo,
            reentregas=reentregas
        )
        db.session.add(entrega)
        db.session.commit()
        recalcular_rotas(rota)
        return redirect("/entregas/")
    rotas_lista = Rotas.query.all()
    funcionarios = Funcionarios.query.all()
    return render_template("/entregas/cadastrar_entrega.html", rotas_lista=rotas_lista, funcionarios=funcionarios)


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
            nova_rota = Rotas(rota=rota, tempo_medio_rota=datetime.strptime(tempo_medio, '%H:%M').time())
            db.session.add(nova_rota)
            db.session.commit()
            return render_template("/entregas/rotas_cadastrar.html", erro='Rota cadastrada')
    except sqlalchemy.exc.IntegrityError:
        db.session.rollback()
        return render_template("/entregas/rotas_cadastrar.html", erro='Erro ao cadastrar')

    return render_template("/entregas/rotas_cadastrar.html")


@app.route('/adm/cadastrar_funcionario', methods=['GET', 'POST'])
def cadastrar_funcionario():
    if request.method == 'POST':
        try:
            nome = request.form['nome']
            funcao = request.form['funcao']
            funcionario = Funcionarios(nome=nome, funcao=funcao)
            db.session.add(funcionario)
            db.session.commit()
            return render_template('/adm/cadastrar_funcionario.html', sucesso='Funcionário cadastrado com sucesso')
        except sqlalchemy.exc.IntegrityError:
            db.session.rollback()
            return render_template('/adm/cadastrar_funcionario.html', erro='Funcionário já existente')
    return render_template('/adm/cadastrar_funcionario.html')


@app.route('/adm/funcionarios', methods=['GET', 'POST'])
def funcionarios():
    funcionarios = Funcionarios.query.all()
    return render_template('/adm/funcionarios.html', funcionarios=funcionarios)


@app.route('/adm/deletar_funcionarios/<int:funcionario_id>', methods=['GET', 'POST'])
def deletar_funcionario(funcionario_id):
    funcionario = Funcionarios.query.filter_by(id=funcionario_id).first()
    db.session.delete(funcionario)
    db.session.commit()
    return redirect(url_for('funcionarios'))


@app.route('/adm/usuarios', methods=["GET", "POST"])
@access_level_required(1)
@login_required
def usuarios():
    usuarios = Users.query.all()
    return render_template("/adm/usuarios.html", usuarios=usuarios)


@app.route('/adm/cadastrar_usuario', methods=["GET", "POST"])
@access_level_required(1)
@login_required
def cadastrar_usuario():
    if request.method == "POST":
        user = Users(username=request.form.get("username"),
                     password=request.form.get("password"), filial=request.form.get("filial"))
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("logar"))
    return render_template("/adm/cadastrar_usuario.html")


@app.route("/logar", methods=["GET", "POST"])
def logar():
    if request.method == "POST":
        user = Users.query.filter_by(
            username=request.form.get("username")).first()
        if user.password == request.form.get("password"):
            login_user(user)
            return redirect(url_for("index"))
    return render_template("logar.html")


@app.route('/entregas/erros', methods=["GET", "POST"])
@access_level_required(1)
@login_required
def erros_de_entrega():
    erros = Erros.query.all()
    return render_template("/entregas/erros.html", erros=erros)


@app.route('/entregas/cadastrar_erro', methods=["GET", "POST"])
@access_level_required(1)
@login_required
def cadastrar_erro():
    funcionarios = Funcionarios.query.all()
    if request.method == "POST":
        data_do_erro = request.form["data_do_erro"]
        erro_funcionario = request.form['erro_funcionario']
        erro_cliente = request.form['erro_cliente']
        quantidade_de_erros = request.form['quantidade_de_erros']
        motorista_da_entrega = request.form['motorista_da_entrega']
        produto_erro = request.form['produto_erro']
        descricao_do_erro = request.form['descricao_do_erro']
        erro = Erros(data_do_erro=data_do_erro, erro_funcionario=erro_funcionario,
                     quantidade_de_erros=quantidade_de_erros, erro_cliente=erro_cliente, produto_erro=produto_erro,
                     motorista_da_entrega=motorista_da_entrega, descricao_do_erro=descricao_do_erro)
        db.session.add(erro)
        db.session.commit()
        return redirect(url_for("cadastrar_erro"))
    return render_template("/entregas/cadastrar_erro.html", funcionarios=funcionarios)


@app.route("/sair")
def sair():
    logout_user()
    return redirect(url_for("logar"))


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
