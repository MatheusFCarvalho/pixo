from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class CacaPixo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    imagem_url = db.Column(db.String(200), nullable=False)
    modo = db.Column(db.String(20), nullable=False)  # single, multiple, text
    palavra_correta = db.Column(db.String(100))
    palavras_multiplas = db.Column(db.Text)  # JSON array como string
    texto_oculto = db.Column(db.Text)
    
    def __repr__(self):
        return f'<CacaPixo {self.titulo}>'