from extensions import db
from datetime import datetime

class TestLog(db.Model):
    __tablename__ = 'test_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id', ondelete='CASCADE'))
    event_type = db.Column(db.String(50), nullable=False)
    event_data = db.Column(db.JSON)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<TestLog {self.event_type}>' 