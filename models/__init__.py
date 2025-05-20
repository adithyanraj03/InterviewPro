# This file makes the models directory a Python package
from extensions import db

# Import all models to make them available when importing from models
from .user import User, user_tests
from .test import Test
from .question import Question
from .interview_question import InterviewQuestion
from .answer import TestAnswer

__all__ = ['User', 'Test', 'Question', 'InterviewQuestion', 'TestAnswer', 'user_tests'] 