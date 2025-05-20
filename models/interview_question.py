from extensions import db
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name

class InterviewQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    code_text = db.Column(db.Text)  # Store actual code text
    code_language = db.Column(db.String(50), default='c')  # Programming language
    option_a = db.Column(db.String(200), nullable=False)
    option_b = db.Column(db.String(200), nullable=False)
    option_c = db.Column(db.String(200), nullable=False)
    option_d = db.Column(db.String(200), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)  # 'A', 'B', 'C', or 'D'
    explanation = db.Column(db.Text)

    def get_highlighted_code(self):
        """Return syntax-highlighted HTML for the code"""
        if not self.code_text:
            print(f"No code text for question {self.id}")
            return None
        
        try:
            print(f"\nHighlighting code for question {self.id}")
            print(f"Code text: '{self.code_text}'")
            print(f"Language: '{self.code_language}'")
            
            lexer = get_lexer_by_name(self.code_language)
            formatter = HtmlFormatter(
                style='monokai',
                linenos=True,
                cssclass='highlight',
                linenostart=1
            )
            highlighted = highlight(self.code_text.strip(), lexer, formatter)
            print(f"Generated HTML: {highlighted[:200]}...")
            return highlighted
        except Exception as e:
            print(f"Error highlighting code: {str(e)}")
            print(f"Full error: {str(e.__class__.__name__)}: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return None 