from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import random
import string

app = Flask(__name__)

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'links.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODELO DA TABELA ---
class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url_original = db.Column(db.String(500), nullable=False)
    url_curta = db.Column(db.String(50), unique=True, nullable=False)
    categoria = db.Column(db.String(50))

# Cria o banco de dados se não existir
with app.app_context():
    db.create_all()

# --- FUNÇÃO AUXILIAR: GERAR CÓDIGO ---
def gerar_codigo():
    caracteres = string.ascii_letters + string.digits
    return ''.join(random.choice(caracteres) for _ in range(6))

# --- ROTA PRINCIPAL (COM A LÓGICA DO DESTAQUE) ---
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url_original = request.form['url_original']
        url_curta = request.form['url_curta']
        categoria = request.form['categoria']

        # Se não escolheu nome, gera automático
        if not url_curta:
            url_curta = gerar_codigo()

        # Verifica se já existe
        link_existente = Link.query.filter_by(url_curta=url_curta).first()
        if link_existente:
             if request.form['url_curta'] == "":
                 url_curta = gerar_codigo() # Tenta de novo se for automático
             else:
                 return "Erro: Esse nome curto já existe!"

        # Salva no banco
        novo_link = Link(url_original=url_original, url_curta=url_curta, categoria=categoria)
        db.session.add(novo_link)
        db.session.commit()
        
        # Redireciona para a home avisando qual é o novo link
        return redirect(url_for('index', novo=url_curta))

    # PARTE DE EXIBIÇÃO (GET)
    links = Link.query.order_by(Link.categoria).all()
    base_url = request.host_url
    
    # Verifica se tem mensagem de "novo link" na URL
    novo_codigo = request.args.get('novo')
    
    return render_template('index.html', links=links, base_url=base_url, novo_link=novo_codigo)

# --- ROTA DE REDIRECIONAMENTO ---
@app.route('/<url_curta>')
def redirecionar(url_curta):
    link = Link.query.filter_by(url_curta=url_curta).first()
    if link:
        return redirect(link.url_original)
    else:
        return "Link não encontrado!"

# --- ROTA DELETAR ---
@app.route('/deletar/<int:id>')
def deletar(id):
    link = Link.query.get_or_404(id)
    db.session.delete(link)
    db.session.commit()
    return redirect('/')

# --- INICIAR O SERVIDOR ---
if __name__ == "__main__":
    app.run(debug=True)