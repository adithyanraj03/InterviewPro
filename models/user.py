from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from extensions import db
from models.test import Test
from models.question import Question
from models.answer import TestAnswer
from models.test_log import TestLog

# Association table for user-test relationship
user_tests = db.Table('user_tests',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE')),
    db.Column('test_id', db.Integer, db.ForeignKey('tests.id', ondelete='CASCADE')),
    db.Column('started_at', db.DateTime, default=datetime.utcnow),
    db.Column('completed_at', db.DateTime),
    db.Column('score', db.Float, nullable=True),
    db.Column('time_spent', db.Integer, default=0)  # Time spent in seconds
)

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(120), nullable=True)
    full_name = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    experience_years = db.Column(db.Integer, nullable=True)
    current_role = db.Column(db.String(100), nullable=True)
    skills = db.Column(db.JSON)
    is_admin = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime)
    login_count = db.Column(db.Integer, default=0)
    last_login_ip = db.Column(db.String(45))
    last_login_device = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_tests = db.relationship('Test', backref='creator', lazy=True)
    
    # Tests taken by this user (candidate)
    taken_tests = db.relationship(
        'Test',
        secondary=user_tests,
        lazy='dynamic',
        backref=db.backref('test_takers', lazy=True)
    )
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def update_last_login(self, ip=None, user_agent=None):
        """Update login history"""
        self.last_login = datetime.utcnow()
        self.login_count += 1
        if ip:
            self.last_login_ip = ip
        if user_agent:
            self.last_login_device = user_agent
        db.session.commit()
        
    def get_test_history(self):
        """Get test history with test details"""
        # Get all test attempts with test details
        stmt = db.select(
            user_tests.c.test_id,
            user_tests.c.started_at,
            user_tests.c.completed_at,
            user_tests.c.score,
            user_tests.c.time_spent,
            Test
        ).join(
            Test, Test.id == user_tests.c.test_id
        ).where(
            user_tests.c.user_id == self.id
        ).order_by(user_tests.c.started_at.desc())
        
        history = []
        result = db.session.execute(stmt)
        
        for row in result:
            # Get security logs for this attempt
            security_logs = TestLog.query.filter_by(
                user_id=self.id,
                test_id=row.test_id
            ).order_by(TestLog.timestamp).all()
            
            # Format security logs
            formatted_logs = [{
                'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'event': log.event_data['event']
            } for log in security_logs]
            
            history.append({
                'test_id': row.test_id,
                'test_title': row.Test.title,
                'test_code': row.Test.test_code,
                'test_duration': row.Test.duration,
                'test_passing_score': row.Test.passing_score,
                'started_at': row.started_at,
                'completed_at': row.completed_at,
                'score': row.score,
                'time_spent': row.time_spent,
                'security_logs': formatted_logs
            })
        
        return history

    def get_active_test(self):
        """Get the currently active test for the candidate, if any"""
        test_record = db.session.query(user_tests).filter_by(
            user_id=self.id,
            completed_at=None
        ).first()
        
        if test_record:
            return Test.query.get(test_record.test_id)
        return None

    def has_test_access(self, test):
        """Check if user has access to a test"""
        return test in self.taken_tests

    def get_remaining_attempts(self, test):
        """Get remaining attempts for a test"""
        completed_attempts = db.session.query(user_tests).filter(
            user_tests.c.user_id == self.id,
            user_tests.c.test_id == test.id,
            user_tests.c.completed_at != None
        ).count()
        return test.max_attempts - completed_attempts

    def can_start_test(self, test):
        """Check if user can start a test"""
        if not self.has_test_access(test):
            return False, "No access to this test"
            
        if self.get_remaining_attempts(test) <= 0:
            return False, "Maximum attempts reached"
            
        # Check for incomplete attempt
        incomplete = db.session.query(user_tests).filter(
            user_tests.c.user_id == self.id,
            user_tests.c.test_id == test.id,
            user_tests.c.completed_at == None
        ).first()
        
        if incomplete:
            return False, "You have an incomplete attempt"
            
        return True, None

    def __repr__(self):
        return f'<User {self.username}>' 