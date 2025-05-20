from extensions import db
from datetime import datetime
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id', ondelete='CASCADE'))
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.Text, nullable=False)
    option_b = db.Column(db.Text, nullable=False)
    option_c = db.Column(db.Text, nullable=False)
    option_d = db.Column(db.Text, nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)
    explanation = db.Column(db.Text)
    code_text = db.Column(db.Text)
    code_language = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Question {self.id}: {self.question_text[:30]}...>'
    
    def get_highlighted_code(self):
        if not self.code_text or not self.code_language:
            return None
        try:
            lexer = get_lexer_by_name(self.code_language, stripall=True)
            formatter = HtmlFormatter(style='monokai', cssclass='highlight')
            return highlight(self.code_text, lexer, formatter)
        except:
            return None
            
    def get_highlight_css(self):
        return HtmlFormatter(style='monokai').get_style_defs('.highlight')

class InterviewQuestion(db.Model):
    __tablename__ = 'interview_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.Text, nullable=False)
    option_b = db.Column(db.Text, nullable=False)
    option_c = db.Column(db.Text, nullable=False)
    option_d = db.Column(db.Text, nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)
    explanation = db.Column(db.Text)
    code_text = db.Column(db.Text)
    code_language = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_highlighted_code(self):
        if not self.code_text or not self.code_language:
            return None
        try:
            lexer = get_lexer_by_name(self.code_language, stripall=True)
            formatter = HtmlFormatter(style='monokai', cssclass='highlight')
            return highlight(self.code_text, lexer, formatter)
        except:
            return None
            
    def get_highlight_css(self):
        return HtmlFormatter(style='monokai').get_style_defs('.highlight') 