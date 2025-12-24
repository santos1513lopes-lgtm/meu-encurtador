from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import random
import string

app = Flask(__name__)

# Configuração do Banco de Dados
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'links.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url_original = db.Column(db.String(500), nullable=False)
    url_curta = db.Column(db.String(50), unique=True, nullable=False)
    categoria = db.Column(db.String(50))

with app.app_context():
    db.create_all()

# --- NOVA FUNÇÃO: Gera código aleatório de 6 caracteres ---
def gerar_codigo():
    caracteres = string.ascii_letters + string.digits # Letras e números
    return ''.join(random.choice(caracteres) for _ in range(6))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url_original = request.form['url_original']
        url_curta = request.form['url_curta']
        categoria = request.form['categoria']

        # Se o usuário deixar em branco, gera automaticamente
        if not url_curta:
            url_curta = gerar_codigo()

        # Verifica duplicidade
        link_existente = Link.query.filter_by(url_curta=url_curta).first()
        if link_existente:
             # Se for automático e der azar de repetir, tenta de novo (recursividade simples)
             if request.form['url_curta'] == "":
                 url_curta = gerar_codigo()
             else:
                 return "Erro: Esse nome curto já existe!"

        novo_link = Link(url_original=url_original, url_curta=url_curta, categoria=categoria)
        db.session.add(novo_link)
        db.session.commit()
        return redirect('/')

    links = Link.query.order_by(Link.categoria).all()
    # Passamos a URL base para facilitar o botão de copiar
    base_url = request.host_url 
    return render_template('index.html', links=links, base_url=base_url)

@app.route('/<url_curta>')
def redirecionar(url_curta):
    link = Link.query.filter_by(url_curta=url_curta).first()
    if link:
        return redirect(link.url_original)
    else:
        return "Link não encontrado!"

# --- NOVA ROTA: Deletar ---
@app.route('/deletar/<int:id>')
def deletar(id):
    link = Link.query.get_or_404(id)
    db.session.delete(link)
    db.session.commit()
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)