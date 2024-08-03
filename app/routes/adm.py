from ..main import *
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


@app.route('/adm/deletar_funcionario/<int:funcionario_id>', methods=['POST'])
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
                     password=request.form.get("password"), filial=request.form.get("filial"), acesso=request.form.get("acesso"))
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


@app.route("/sair")
def sair():
    logout_user()
    return redirect(url_for("logar"))

