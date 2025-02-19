from ..main import *

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


def calcular_porcentagem(valor_inicial, valor_final):
    if valor_inicial == 0:
        aumento = valor_final * 100
        return f"{round(aumento)}%"

    variacao = ((valor_final - valor_inicial) / valor_inicial) * 100

    if variacao > 0:
        return f"+{round(variacao)}%"
    elif variacao < 0:
        return f"{round(variacao)}%"
    else:
        return "0%"

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

def recalcularMediaRota(tempo):
    int(horas = tempo // 3600)
    int(minutos = (tempo % 3600) // 60)
    int(segundos = tempo % 60)
    print(horas, minutos, segundos)
    tempoString = time(int(horas), int(minutos), int(segundos))
    
    return tempoString