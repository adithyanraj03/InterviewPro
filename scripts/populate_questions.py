from app import create_app
from extensions import db
from models.interview_question import InterviewQuestion

questions_data = [
    {
        "category": "Basic Programming Concepts",
        "question_text": "What is the primary purpose of a constructor in object-oriented programming?",
        "option_a": "To destroy objects",
        "option_b": "To initialize object properties",
        "option_c": "To define class methods",
        "option_d": "To handle exceptions",
        "correct_answer": "B",
        "explanation": "A constructor is a special method used to initialize new objects and set their initial state."
    },
    # Add all other questions following the same format...
]

def populate_questions():
    app = create_app()
    with app.app_context():
        # Clear existing questions
        InterviewQuestion.query.delete()
        
        # Add all questions
        for question_data in questions_data:
            question = InterviewQuestion(**question_data)
            db.session.add(question)
        
        db.session.commit()
        print("Questions populated successfully!")

if __name__ == "__main__":
    populate_questions() 