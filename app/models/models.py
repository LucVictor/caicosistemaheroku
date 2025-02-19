from ..main import *
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
    atualizacao = db.Column(db.Date)
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
    usoeconsumo = db.Column(db.String(300), nullable=True)


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
    conferente = db.Column(db.String(250), nullable=True)
    rota = db.Column(db.String(250), nullable=False)
    quantidade_de_entregas = db.Column(db.Integer, nullable=False)
    tempo_total = db.Column(db.Time, nullable=False)
    tempo_total_entrega = db.Column(db.Time, nullable=False)
    tempo_medio_total = db.Column(db.Time, nullable=False)
    tempo_medio_entrega = db.Column(db.Time, nullable=False)
    resultado_tempo = db.Column(db.String(250), nullable=False)
    reentregas = db.Column(db.Integer, nullable=True)
    entreganrealizadas = db.Column(db.Integer, nullable=True)


class Rotas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rota = db.Column(db.String(250), unique=True, nullable=False)
    tempo_medio_rota = db.Column(db.Time, nullable=False)
    total_de_entregas = db.Column(db.Integer,  nullable=True)
    


class Funcionarios(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(250), unique=True, nullable=False)
    funcao = db.Column(db.String(250), nullable=False)

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


class Erros_Vendas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_do_erro = db.Column(db.Date, nullable=False)
    erro_funcionario = db.Column(db.String(250), nullable=False)
    erro_cliente = db.Column(db.String(250), nullable=False)
    quantidade_de_erros = db.Column(db.Integer, nullable=False)
    motorista_da_entrega = db.Column(db.String(250), nullable=False)
    produto_erro = db.Column(db.String(250), nullable=False)
    descricao_do_erro = db.Column(db.String(1000), nullable=True)
    criador = db.Column(db.String(250), nullable=True)


class Erros_Logistica(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_do_erro = db.Column(db.Date, nullable=False)
    erro_funcionario = db.Column(db.String(250), nullable=False)
    erro_cliente = db.Column(db.String(250), nullable=False)
    quantidade_de_erros = db.Column(db.Integer, nullable=False)
    motorista_da_entrega = db.Column(db.String(250), nullable=False)
    rota_da_entrega = db.Column(db.String(250), nullable=False)
    produto_erro = db.Column(db.String(250), nullable=False)
    descricao_do_erro = db.Column(db.String(1000), nullable=True)
    criador = db.Column(db.String(250), nullable=True)

