from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Configuração do Banco de Dados
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'links.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo (Tabela)
class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url_original = db.Column(db.String(500), nullable=False)
    url_curta = db.Column(db.String(50), unique=True, nullable=False)
    categoria = db.Column(db.String(50))

# Cria o banco ao iniciar
with app.app_context():
    db.create_all()

# Rotas
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url_original = request.form['url_original']
        url_curta = request.form['url_curta']
        categoria = request.form['categoria']

        # Verifica se o link curto já existe
        link_existente = Link.query.filter_by(url_curta=url_curta).first()
        if link_existente:
            return "Erro: Esse nome curto já existe! Volte e tente outro."

        novo_link = Link(url_original=url_original, url_curta=url_curta, categoria=categoria)
        
        db.session.add(novo_link)
        db.session.commit()
        return redirect('/')

    links = Link.query.order_by(Link.categoria).all()
    return render_template('index.html', links=links)

@app.route('/<url_curta>')
def redirecionar(url_curta):
    link = Link.query.filter_by(url_curta=url_curta).first()
    if link:
        return redirect(link.url_original)
    else:
        return "Link não encontrado!"

if __name__ == "__main__":
    app.run(debug=True)