from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from models import db, CacaPixo
from forms import CacaPixoForm
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///caca_pixo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
def index():
    caca_pixos = CacaPixo.query.all()
    return render_template('index.html', caca_pixos=caca_pixos)

@app.route('/admin')
def admin():
    caca_pixos = CacaPixo.query.all()
    return render_template('admin.html', caca_pixos=caca_pixos)

@app.route('/create', methods=['GET', 'POST'])
def create():
    form = CacaPixoForm()
    if form.validate_on_submit():
        caca_pixo = CacaPixo(
            titulo=form.titulo.data,
            imagem_url=form.imagem_url.data,
            modo=form.modo.data,
            palavra_correta=form.palavra_correta.data,
            palavras_multiplas=json.dumps(form.palavras_multiplas.data.split(',') if form.palavras_multiplas.data else []),
            texto_oculto=form.texto_oculto.data
        )
        db.session.add(caca_pixo)
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template('create.html', form=form)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    caca_pixo = CacaPixo.query.get_or_404(id)
    form = CacaPixoForm(obj=caca_pixo)
    
    if form.validate_on_submit():
        caca_pixo.titulo = form.titulo.data
        caca_pixo.imagem_url = form.imagem_url.data
        caca_pixo.modo = form.modo.data
        caca_pixo.palavra_correta = form.palavra_correta.data
        caca_pixo.palavras_multiplas = json.dumps(form.palavras_multiplas.data.split(',') if form.palavras_multiplas.data else [])
        caca_pixo.texto_oculto = form.texto_oculto.data
        
        db.session.commit()
        return redirect(url_for('admin'))
    
    # Preencher campos específicos
    if caca_pixo.palavras_multiplas:
        form.palavras_multiplas.data = ','.join(json.loads(caca_pixo.palavras_multiplas))
    
    return render_template('edit.html', form=form, caca_pixo=caca_pixo)

@app.route('/delete/<int:id>')
def delete(id):
    caca_pixo = CacaPixo.query.get_or_404(id)
    db.session.delete(caca_pixo)
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/play/<int:id>')
def play(id):
    caca_pixo = CacaPixo.query.get_or_404(id)
    session['current_game'] = id
    session['found_words'] = []
    session['revealed_text'] = '_' * len(caca_pixo.texto_oculto) if caca_pixo.texto_oculto else ''
    
    if caca_pixo.modo == 'single':
        return render_template('game_modes/single.html', caca_pixo=caca_pixo)
    elif caca_pixo.modo == 'multiple':
        return render_template('game_modes/multiple.html', caca_pixo=caca_pixo)
    elif caca_pixo.modo == 'text':
        return render_template('game_modes/text.html', caca_pixo=caca_pixo)

@app.route('/check_answer', methods=['POST'])
def check_answer():
    data = request.get_json()
    game_id = session.get('current_game')
    resposta = data.get('resposta', '').strip().lower()
    
    caca_pixo = CacaPixo.query.get(game_id)
    
    if caca_pixo.modo == 'single':
        if resposta == caca_pixo.palavra_correta.lower():
            return jsonify({'correct': True, 'message': 'Parabéns! Você acertou!'})
        else:
            return jsonify({'correct': False, 'message': 'Tente novamente!'})
    
    elif caca_pixo.modo == 'multiple':
        palavras = json.loads(caca_pixo.palavras_multiplas)
        found_words = session.get('found_words', [])
        
        if resposta in palavras and resposta not in found_words:
            found_words.append(resposta)
            session['found_words'] = found_words
            
            if len(found_words) == len(palavras):
                return jsonify({
                    'correct': True, 
                    'message': f'Parabéns! Você encontrou todas as {len(palavras)} palavras!',
                    'found_words': found_words,
                    'completed': True
                })
            else:
                return jsonify({
                    'correct': True, 
                    'message': f'Correto! Encontrou {len(found_words)} de {len(palavras)} palavras.',
                    'found_words': found_words,
                    'completed': False
                })
        elif resposta in found_words:
            return jsonify({'correct': False, 'message': 'Você já encontrou esta palavra!'})
        else:
            return jsonify({'correct': False, 'message': 'Palavra não encontrada. Tente outra!'})
    
    elif caca_pixo.modo == 'text':
        texto_original = caca_pixo.texto_oculto.lower()
        palavra = resposta.lower()
        revealed_text = session.get('revealed_text', '_' * len(texto_original))
        
        if palavra in texto_original:
            # Revelar a palavra no texto
            new_revealed = list(revealed_text)
            start_index = 0
            while True:
                index = texto_original.find(palavra, start_index)
                if index == -1:
                    break
                
                for i in range(index, index + len(palavra)):
                    new_revealed[i] = caca_pixo.texto_oculto[i]
                
                start_index = index + len(palavra)
            
            session['revealed_text'] = ''.join(new_revealed)
            
            if '_' not in session['revealed_text']:
                return jsonify({
                    'correct': True,
                    'message': 'Parabéns! Você completou todo o texto!',
                    'revealed_text': session['revealed_text'],
                    'completed': True
                })
            else:
                return jsonify({
                    'correct': True,
                    'message': f'Palavra encontrada! Texto revelado: {session["revealed_text"]}',
                    'revealed_text': session['revealed_text'],
                    'completed': False
                })
        else:
            return jsonify({'correct': False, 'message': 'Palavra não encontrada no texto.'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)