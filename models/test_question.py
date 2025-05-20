from extensions import db
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, TextLexer

class TestQuestion(db.Model):
    __tablename__ = 'test_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id', ondelete='CASCADE'), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    code_text = db.Column(db.Text)
    code_language = db.Column(db.String(50))
    option_a = db.Column(db.Text, nullable=False)
    option_b = db.Column(db.Text, nullable=False)
    option_c = db.Column(db.Text, nullable=False)
    option_d = db.Column(db.Text, nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)
    explanation = db.Column(db.Text)
    
    def __init__(self, question_data):
        self.category = question_data.category
        self.question_text = question_data.question_text
        self.code_text = question_data.code_text
        self.code_language = question_data.code_language
        self.option_a = question_data.option_a
        self.option_b = question_data.option_b
        self.option_c = question_data.option_c
        self.option_d = question_data.option_d
        self.correct_answer = question_data.correct_answer
        self.explanation = question_data.explanation
        
    def get_highlighted_code(self):
        """Return syntax-highlighted code if code_text exists"""
        if not self.code_text:
            return None
            
        try:
            lexer = get_lexer_by_name(self.code_language or 'text')
        except:
            lexer = TextLexer()
            
        formatter = HtmlFormatter(style='monokai', 
                                cssclass='highlight',
                                linenos=True)
                                
        return highlight(self.code_text, lexer, formatter)
        
    def get_highlight_css(self):
        """Return CSS for syntax highlighting"""
        formatter = HtmlFormatter(style='monokai')
        return formatter.get_style_defs('.highlight') 