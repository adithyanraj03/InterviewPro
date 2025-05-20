from datetime import datetime
from extensions import db
import random
import string

class Test(db.Model):
    __tablename__ = 'tests'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    test_code = db.Column(db.String(10), unique=True, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # in minutes
    passing_score = db.Column(db.Integer, nullable=False)  # percentage
    max_attempts = db.Column(db.Integer, default=1)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    questions = db.relationship('Question', backref='test', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Test {self.title}>'
    
    def get_duration_text(self):
        """Return human-readable duration"""
        if self.duration < 60:
            return f"{self.duration} minutes"
        hours = self.duration // 60
        minutes = self.duration % 60
        if minutes == 0:
            return f"{hours} hour{'s' if hours > 1 else ''}"
        return f"{hours} hour{'s' if hours > 1 else ''} {minutes} minutes"

    @staticmethod
    def generate_test_code():
        """Generate a unique 8-character test code"""
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            if not Test.query.filter_by(test_code=code).first():
                return code 