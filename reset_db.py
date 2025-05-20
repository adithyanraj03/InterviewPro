from app import create_app, db
from models.user import User
from models.test import Test
from models.question import Question, InterviewQuestion
from models.test_log import TestLog

app = create_app()

def reset_database():
    with app.app_context():
        # Drop all tables
        db.drop_all()
        
        # Create all tables
        db.create_all()
          # Create admin user
        admin = User(username='admin', is_admin=True)
        admin.set_password('admin123')  # Already updated to match README
        db.session.add(admin)
        db.session.commit()
        
        # Create sample questions
        questions = [
            InterviewQuestion(
                category="Python",
                question_text="What is a list comprehension in Python?",
                option_a="A way to create lists using a compact syntax",
                option_b="A method to sort lists",
                option_c="A function to filter lists",
                option_d="A class that inherits from list",
                correct_answer="A",
                explanation="List comprehension provides a concise way to create lists based on existing lists or other iterables."
            ),
            InterviewQuestion(
                category="Python",
                question_text="What will be the output of this code?",
                code_text="x = [1, 2, 3]\ny = x\ny.append(4)\nprint(x)",
                code_language="python",
                option_a="[1, 2, 3]",
                option_b="[1, 2, 3, 4]",
                option_c="Error",
                option_d="None",
                correct_answer="B",
                explanation="In Python, variables hold references to objects. When y = x is executed, both variables reference the same list."
            )
        ]
        
        for question in questions:
            db.session.add(question)
        db.session.commit()
        
        # Create sample test
        test = Test(
            title="Python Basics",
            description="Test your Python programming knowledge",
            duration=30,
            passing_score=70,
            max_attempts=2,
            created_by=admin.id,
            test_code=Test.generate_test_code()
        )
        db.session.add(test)
        db.session.commit()
        
        # Add questions to test
        for q in questions:
            test_question = Question(
                test_id=test.id,
                question_text=q.question_text,
                option_a=q.option_a,
                option_b=q.option_b,
                option_c=q.option_c,
                option_d=q.option_d,
                correct_answer=q.correct_answer,
                explanation=q.explanation,
                code_text=q.code_text,
                code_language=q.code_language
            )
            db.session.add(test_question)
        db.session.commit()
        
        print("Created admin user with username: admin, password: admin123")
        print(f"Created test with code: {test.test_code}")
        print("Database reset complete!")

if __name__ == "__main__":
    reset_database() 