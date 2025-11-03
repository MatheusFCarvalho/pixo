from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

class CacaPixoForm(FlaskForm):
    titulo = StringField('Título', validators=[DataRequired()])
    imagem_url = StringField('URL da Imagem', validators=[DataRequired()])
    modo = SelectField('Modo de Jogo', 
                      choices=[('single', 'Modo Único'), 
                              ('multiple', 'Modo Múltiplo'), 
                              ('text', 'Modo Texto')],
                      validators=[DataRequired()])
    palavra_correta = StringField('Palavra Correta (Modo Único)')
    palavras_multiplas = StringField('Palavras (Modo Múltiplo - separadas por vírgula)')
    texto_oculto = TextAreaField('Texto Oculto (Modo Texto)')
    submit = SubmitField('Salvar')