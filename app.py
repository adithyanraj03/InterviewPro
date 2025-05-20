from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, send_file, Response
from flask_login import login_user, logout_user, login_required, current_user
from config import Config
from extensions import db, login_manager
from models import *  # This will import everything defined in __all__
from datetime import datetime, timedelta
import json
import csv
from io import StringIO
from functools import wraps
import random
import os
import pygments
from pygments.formatters import HtmlFormatter
from pygments.lexers import CLexer
from PIL import Image, ImageDraw, ImageFont
import io
from pygments import highlight
from pygments.formatters import ImageFormatter
from pygments.lexers import get_lexer_by_name
from models.test_log import TestLog


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'index'

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    @app.route('/')
    def index():
        if current_user.is_authenticated:
            if current_user.is_admin:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('candidate_dashboard'))
        return render_template('auth/login.html')

    @app.route('/login', methods=['POST'])
    def login():
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            # Get IP and user agent
            ip = request.remote_addr
            user_agent = request.user_agent.string
            user.update_last_login(ip=ip, user_agent=user_agent)
            
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('candidate_dashboard'))
        
        flash('Invalid username or password')
        return redirect(url_for('index'))

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('index'))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            # Check if username already exists
            existing_user = User.query.filter_by(username=request.form['username']).first()
            if existing_user:
                flash('Username already exists. Please choose a different username.')
                return redirect(url_for('register'))

            try:
                user = User(
                    username=request.form['username'],
                    email=request.form['email'],
                    full_name=request.form['full_name'],
                    phone=request.form['phone'],
                    experience_years=int(request.form['experience_years']),
                    current_role=request.form['current_role'],
                    skills=[],  # Initialize empty skills array
                    is_admin=False
                )
                user.set_password(request.form['password'])
                db.session.add(user)
                db.session.commit()
                flash('Registration successful! Please login.')
                return redirect(url_for('index'))
            except Exception as e:
                db.session.rollback()
                flash('An error occurred during registration. Please try again.')
                return redirect(url_for('register'))

        return render_template('auth/register.html')

    def admin_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or not current_user.is_admin:
                flash('Please login as admin to access this page.')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function

    @app.route('/admin/dashboard')
    @admin_required
    def admin_dashboard():
        if not current_user.is_admin:
            return redirect(url_for('candidate_dashboard'))
        
        # Get basic statistics
        questions = InterviewQuestion.query.all()
        tests = Test.query.all()
        candidates = User.query.filter_by(is_admin=False).all()
        
        # Mock recent activities (replace with real data from database)
        recent_activities = [
            {
                'icon': 'fas fa-user-plus',
                'description': 'New candidate registered',
                'time': '5 minutes ago'
            },
            {
                'icon': 'fas fa-file-alt',
                'description': 'New test created: Python Basics',
                'time': '1 hour ago'
            },
            {
                'icon': 'fas fa-check-circle',
                'description': 'Test completed by John Doe',
                'time': '2 hours ago'
            }
        ]
        
        return render_template('admin/dashboard.html',
            questions=questions,
            tests=tests,
            candidates=candidates,
            recent_activities=recent_activities
        )

    @app.route('/admin/create-test', methods=['GET', 'POST'])
    @admin_required
    def create_test():
        if request.method == 'POST':
            try:
                test = Test(
                    title=request.form['title'],
                    description=request.form['description'],
                    duration=int(request.form['duration']),
                    passing_score=int(request.form['passing_score']),
                    max_attempts=int(request.form['max_attempts']),
                    created_by=current_user.id,
                    test_code=Test.generate_test_code()
                )
                db.session.add(test)
                db.session.commit()

                selected_questions = request.form.get('selected_questions', '').split(',')
                # Remove any duplicates
                selected_questions = list(set(selected_questions))
                
                if selected_questions and selected_questions[0]:
                    for question_id in selected_questions:
                        question = InterviewQuestion.query.get(int(question_id))
                        if question:
                            test_question = Question(
                                test_id=test.id,
                                question_text=question.question_text,
                                option_a=question.option_a,
                                option_b=question.option_b,
                                option_c=question.option_c,
                                option_d=question.option_d,
                                correct_answer=question.correct_answer,
                                explanation=question.explanation,
                                code_text=question.code_text,
                                code_language=question.code_language
                            )
                            db.session.add(test_question)
                    db.session.commit()

                flash('Test created successfully!', 'success')
                return redirect(url_for('preview_test', test_id=test.id))
            except Exception as e:
                db.session.rollback()
                print(f"Error creating test: {str(e)}")
                flash(f'Error creating test: {str(e)}', 'error')
                return redirect(url_for('create_test'))

        # GET request - show form
        questions = [
            {
                'id': q.id,
                'category': q.category,
                'question_text': q.question_text,
                'option_a': q.option_a,
                'option_b': q.option_b,
                'option_c': q.option_c,
                'option_d': q.option_d,
                'correct_answer': q.correct_answer,
                'code_text': q.code_text,
                'code_language': q.code_language
            } for q in InterviewQuestion.query.all()
        ]
        categories = sorted(set(q['category'] for q in questions))
        
        return render_template('admin/create_test.html', 
                             questions=questions,
                             categories=categories)

    @app.route('/admin/candidates')
    @admin_required
    def view_candidates():
        candidates = User.query.filter_by(is_admin=False)\
            .outerjoin(user_tests)\
            .all()
        
        # Add test attempts to each candidate
        for candidate in candidates:
            attempts_query = db.session.query(user_tests.c.score,
                                            user_tests.c.completed_at,
                                            user_tests.c.time_spent,
                                            Test)\
                .join(Test, Test.id == user_tests.c.test_id)\
                .filter(
                    user_tests.c.user_id == candidate.id,
                    user_tests.c.completed_at != None
                )\
                .order_by(user_tests.c.completed_at.desc())\
                .all()
            
            # Convert query results to a list of dictionaries
            candidate.test_attempts = []
            for score, completed_at, time_spent, test in attempts_query:
                candidate.test_attempts.append({
                    'score': score,
                    'completed_at': completed_at,
                    'time_spent': time_spent,
                    'test': test
                })
        
        return render_template('admin/candidates.html', candidates=candidates)

    @app.route('/admin/analytics')
    @login_required
    def analytics():
        if not current_user.is_admin:
            return redirect(url_for('candidate_dashboard'))
        return render_template('admin/analytics.html')

    @app.route('/candidate/dashboard')
    @login_required
    def candidate_dashboard():
        if current_user.is_admin:
            return redirect(url_for('admin_dashboard'))
        tests = current_user.taken_tests
        return render_template('candidate/dashboard.html', tests=tests)

    @app.route('/admin/questions')
    @admin_required
    def admin_questions():
        # Get all questions and ensure code_text is loaded
        questions = InterviewQuestion.query.order_by(InterviewQuestion.id.desc()).all()
        # Clean up empty code_text fields
        for question in questions:
            if question.code_text and not question.code_text.strip():
                question.code_text = None
                question.code_language = None
        db.session.commit()
        return render_template('admin/questions.html', questions=questions)

    @app.route('/admin/questions/add', methods=['GET', 'POST'])
    @login_required
    def add_question():
        if not current_user.is_admin:
            return redirect(url_for('candidate_dashboard'))
        
        if request.method == 'POST':
            print("\nAdding new question:")
            print(f"Code text: {request.form.get('code_text', '')}")
            print(f"Language: {request.form.get('code_language', 'c')}")
            
            question = InterviewQuestion(
                category=request.form['category'],
                question_text=request.form['question_text'],
                code_text=request.form.get('code_text', '').strip(),
                code_language=request.form.get('code_language', 'c'),
                option_a=request.form['option_a'],
                option_b=request.form['option_b'],
                option_c=request.form['option_c'],
                option_d=request.form['option_d'],
                correct_answer=request.form['correct_answer'].upper(),
                explanation=request.form['explanation']
            )
            db.session.add(question)
            db.session.commit()
            print(f"Added question with ID: {question.id}")
            flash('Question added successfully!')
            return redirect(url_for('admin_questions'))
        
        return render_template('admin/add_question.html')

    @app.route('/api/questions/<int:question_id>')
    @login_required
    def get_question(question_id):
        if not current_user.is_admin:
            return jsonify({'error': 'Unauthorized'}), 403
        
        question = InterviewQuestion.query.get_or_404(question_id)
        return jsonify({
            'id': question.id,
            'category': question.category,
            'question_text': question.question_text,
            'option_a': question.option_a,
            'option_b': question.option_b,
            'option_c': question.option_c,
            'option_d': question.option_d,
            'correct_answer': question.correct_answer,
            'explanation': question.explanation
        })

    @app.route('/api/candidates/<int:candidate_id>')
    @login_required
    def get_candidate(candidate_id):
        if not current_user.is_admin:
            return jsonify({'error': 'Unauthorized'}), 403
        
        candidate = User.query.get_or_404(candidate_id)
        return jsonify({
            'id': candidate.id,
            'username': candidate.username,
            'created_at': candidate.created_at.strftime('%Y-%m-%d'),
            'tests_taken': len(candidate.tests),
            'average_score': calculate_average_score(candidate),
            'status': get_candidate_status(candidate)
        })

    @app.route('/api/candidates/<int:candidate_id>/report')
    @login_required
    def download_candidate_report(candidate_id):
        if not current_user.is_admin:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Generate PDF report (you'll need to implement this)
        # For now, return a dummy file
        return send_file(
            'static/reports/dummy.pdf',
            as_attachment=True,
            download_name=f'candidate_{candidate_id}_report.pdf'
        )

    @app.route('/api/candidates/<int:candidate_id>', methods=['DELETE'])
    @login_required
    def delete_candidate(candidate_id):
        if not current_user.is_admin:
            return jsonify({'error': 'Unauthorized'}), 403
        
        candidate = User.query.get_or_404(candidate_id)
        db.session.delete(candidate)
        db.session.commit()
        return '', 204

    @app.route('/api/analytics/data')
    @login_required
    def get_analytics_data():
        if not current_user.is_admin:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Get date range
        days = int(request.args.get('days', 7))
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get analytics data
        data = {
            'completion_trend': get_completion_trend(start_date, end_date),
            'score_distribution': get_score_distribution(),
            'category_performance': get_category_performance(),
            'challenging_questions': get_challenging_questions()
        }
        
        return jsonify(data)

    @app.route('/api/questions/import', methods=['POST'])
    @login_required
    def import_questions():
        if not current_user.is_admin:
            return jsonify({'error': 'Unauthorized'}), 403

        questions = request.json.get('questions', [])
        try:
            # Clear existing questions first
            InterviewQuestion.query.delete()
            db.session.commit()

            for q in questions:
                # Handle code fields properly
                code_text = None
                code_language = None
                
                if 'code_text' in q and q['code_text'] and q['code_text'].strip():
                    # Format the code with proper indentation
                    code_lines = q['code_text'].strip().split('\n')
                    # Remove common leading whitespace
                    while code_lines and not code_lines[0].strip():
                        code_lines.pop(0)
                    while code_lines and not code_lines[-1].strip():
                        code_lines.pop()
                    
                    if code_lines:
                        # Find minimum indentation
                        min_indent = float('inf')
                        for line in code_lines:
                            if line.strip():  # Only check non-empty lines
                                indent = len(line) - len(line.lstrip())
                                min_indent = min(min_indent, indent)
                        
                        # Remove the common indentation
                        if min_indent < float('inf'):
                            code_lines = [line[min_indent:] if line.strip() else '' for line in code_lines]
                        
                        code_text = '\n'.join(code_lines)
                    code_language = q.get('code_language', 'c')

                question = InterviewQuestion(
                    category=q['category'],
                    question_text=q['question_text'],
                    code_text=code_text,
                    code_language=code_language,
                    option_a=q['option_a'],
                    option_b=q['option_b'],
                    option_c=q['option_c'],
                    option_d=q['option_d'],
                    correct_answer=q['correct_answer'].upper(),
                    explanation=q['explanation']
                )
                db.session.add(question)
            db.session.commit()
            flash('Questions imported successfully!')
            return jsonify({'success': True, 'count': len(questions)})
        except Exception as e:
            db.session.rollback()
            flash(f'Error importing questions: {str(e)}')
            return jsonify({'success': False, 'error': str(e)})

    @app.route('/admin/populate_questions')
    @admin_required
    def populate_questions():
        try:
            # Clear existing questions
            InterviewQuestion.query.delete()
            
            # Read questions from JSON file
            with open('static/data/questions.json', 'r') as f:
                data = json.load(f)
            
            print("\nPopulating questions from JSON:")
            # Add questions to database
            for q in data['questions']:
                # Handle code fields properly
                code_text = None
                code_language = None
                
                print(f"\nProcessing question: {q['question_text'][:50]}...")
                print(f"Code text in JSON: {q.get('code_text', 'None')}")
                print(f"Code language in JSON: {q.get('code_language', 'None')}")
                
                if 'code_text' in q and q['code_text'] and q['code_text'].strip():
                    # Format the code with proper indentation
                    code_lines = q['code_text'].strip().split('\n')
                    # Remove common leading whitespace
                    while code_lines and not code_lines[0].strip():
                        code_lines.pop(0)
                    while code_lines and not code_lines[-1].strip():
                        code_lines.pop()
                    
                    if code_lines:
                        # Find minimum indentation
                        min_indent = float('inf')
                        for line in code_lines:
                            if line.strip():  # Only check non-empty lines
                                indent = len(line) - len(line.lstrip())
                                min_indent = min(min_indent, indent)
                        
                        # Remove the common indentation
                        if min_indent < float('inf'):
                            code_lines = [line[min_indent:] if line.strip() else '' for line in code_lines]
                        
                        code_text = '\n'.join(code_lines)
                    code_language = q.get('code_language', 'c')
                    print(f"Setting code_text: {code_text[:50]}...")
                    print(f"Setting code_language: {code_language}")
                
                question = InterviewQuestion(
                    category=q['category'],
                    question_text=q['question_text'],
                    code_text=code_text,
                    code_language=code_language,
                    option_a=q['option_a'],
                    option_b=q['option_b'],
                    option_c=q['option_c'],
                    option_d=q['option_d'],
                    correct_answer=q['correct_answer'],
                    explanation=q.get('explanation', '')
                )
                db.session.add(question)
                print(f"Added question with code: {code_text is not None}")
            
            db.session.commit()
            print("\nSuccessfully committed all questions")
            flash('Questions populated successfully!')
            return redirect(url_for('admin_questions'))
            
        except Exception as e:
            print(f"\nError populating questions: {str(e)}")
            db.session.rollback()
            flash(f'Error populating questions: {str(e)}')
            return redirect(url_for('admin_questions'))

    @app.route('/download/json-template')
    @login_required
    def download_json_template():
        if not current_user.is_admin:
            return redirect(url_for('candidate_dashboard'))

        template = {
            "questions": [
                {
                    "category": "Basic Programming",
                    "question_text": "What is a variable?",
                    "code_text": "int main() {\n    int x = 5;\n    printf(\"%d\", x);\n    return 0;\n}",
                    "code_language": "c",
                    "option_a": "A container for data",
                    "option_b": "A loop construct",
                    "option_c": "A function name",
                    "option_d": "A class definition",
                    "correct_answer": "A",
                    "explanation": "A variable is a named container that stores data in programming."
                }
            ]
        }

        return Response(
            json.dumps(template, indent=4),
            mimetype='application/json',
            headers={'Content-Disposition': 'attachment;filename=question_template.json'}
        )

    @app.route('/candidate/test/<int:test_id>', methods=['GET'])
    @login_required
    def take_test(test_id):
        if current_user.is_admin:
            return redirect(url_for('admin_dashboard'))
        
        app.logger.info(f"User {current_user.username} attempting to access test {test_id}")
        test = Test.query.get_or_404(test_id)
        
        # Check if user has access to this test
        if test not in current_user.taken_tests:
            flash('You do not have access to this test.', 'error')
            return redirect(url_for('candidate_dashboard'))
        
        # Check if test is already completed
        test_record = db.session.query(user_tests).filter_by(
            user_id=current_user.id,
            test_id=test.id,
            completed_at=None
        ).first()
        
        # Fetch unique questions with proper ordering
        questions = Question.query.filter_by(test_id=test.id)\
            .distinct(Question.id)\
            .order_by(Question.id)\
            .all()
        
        # Verify we have the correct number of questions
        app.logger.info(f"Fetched {len(questions)} questions for test {test_id}")
        
        if not questions:
            flash('This test has no questions. Please contact an administrator.', 'error')
            return redirect(url_for('candidate_dashboard'))
        
        # Shuffle options for each question
        for question in questions:
            options = [
                ('A', question.option_a),
                ('B', question.option_b),
                ('C', question.option_c),
                ('D', question.option_d)
            ]
            random.shuffle(options)
            question.shuffled_options = options
        
        if test_record:
            # Test already started, continue
            return render_template('candidate/test.html', 
                                 test=test,
                                 questions=questions,
                                 time_spent=test_record.time_spent)
            
        # Check attempts
        completed_attempts = db.session.query(user_tests).filter(
            user_tests.c.user_id == current_user.id,
            user_tests.c.test_id == test.id,
            user_tests.c.completed_at != None
        ).count()
        
        if completed_attempts >= test.max_attempts:
            flash('You have reached the maximum number of attempts for this test.', 'error')
            return redirect(url_for('candidate_dashboard'))
            
        try:
            # Clear any incomplete attempts
            db.session.query(user_tests).filter(
                user_tests.c.user_id == current_user.id,
                user_tests.c.test_id == test.id,
                user_tests.c.completed_at == None
            ).delete()
            
            # Create new test attempt
            stmt = user_tests.insert().values(
                user_id=current_user.id,
                test_id=test.id,
                started_at=datetime.utcnow()
            )
            db.session.execute(stmt)
            db.session.commit()
            
            return render_template('candidate/test.html', test=test, questions=questions)
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Database error: {str(e)}")
            flash('Error starting test. Please try again.', 'error')
            return redirect(url_for('candidate_dashboard'))

    @app.route('/admin/test/preview/<int:test_id>')
    @admin_required
    def preview_test(test_id):
        test = Test.query.get_or_404(test_id)
        questions = Question.query.filter_by(test_id=test_id).all()
        return render_template('admin/test_preview.html', test=test, questions=questions)

    @app.route('/check-username')
    def check_username():
        username = request.args.get('username')
        user = User.query.filter_by(username=username).first()
        return jsonify({'exists': user is not None})

    @app.route('/code-image/<int:question_id>')
    def code_image(question_id):
        question = InterviewQuestion.query.get_or_404(question_id)
        print(f"\nGenerating code image for question {question_id}")
        print(f"Code text: '{question.code_text}'")
        print(f"Language: '{question.code_language}'")
        
        if not question.code_text:
            print("No code text found")
            return ''

        try:
            # Get the appropriate lexer for the language
            lexer = get_lexer_by_name(question.code_language)
            
            # Create formatter with custom styles
            formatter = ImageFormatter(
                style='monokai',
                line_numbers=True,
                font_size=18,
                line_pad=10,
                background_color='#1e1e1e',
                line_number_bg='#252525',
                line_number_fg='#808080',
                line_number_pad=16,
                line_number_separator=True,
                hl_color='#3c3c3c',
                hl_lines=set(),
                font_name='Consolas',
                image_pad=25,
                image_border=2,
                line_number_bold=True,
                line_number_chars=2,
                image_format='PNG',
                line_number_start=1,
                line_number_step=1,
                line_number_separator_px=2
            )
            
            # Generate image
            code_text = question.code_text.strip()
            image_bytes = highlight(code_text, lexer, formatter)
            
            print("Successfully generated code image")
            return Response(
                image_bytes,
                mimetype='image/png',
                headers={
                    'Cache-Control': 'no-cache, no-store, must-revalidate',
                    'Pragma': 'no-cache',
                    'Expires': '0'
                }
            )

        except Exception as e:
            print(f"Error generating code image: {str(e)}")
            print(f"Full error: {str(e.__class__.__name__)}: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return ''

    @app.route('/candidate/submit-test', methods=['POST'])
    @login_required
    def submit_test():
        try:
            test_id = request.form.get('test_id')
            if not test_id:
                app.logger.error("No test_id provided in form data")
                return jsonify({'error': 'No test ID provided'}), 400
            
            test_id = int(test_id)
            time_spent = request.form.get('time_spent', 0)
            test = Test.query.get_or_404(test_id)
            
            # Get all answers
            answers = []
            score = 0
            total_questions = len(test.questions)
            
            for question in test.questions:
                answer = request.form.get(f'answer_{question.id}')
                if not answer:
                    continue  # Skip unanswered questions
                
                is_correct = answer == question.correct_answer
                if is_correct:
                    score += 1
                    
                # Save answer
                test_answer = TestAnswer(
                    user_id=current_user.id,
                    test_id=test.id,
                    question_id=question.id,
                    answer=answer,
                    is_correct=is_correct
                )
                db.session.add(test_answer)
                answers.append(test_answer)
            
            # Calculate percentage score
            percentage_score = round((score / total_questions) * 100, 2) if total_questions > 0 else 0
            
            # Update test completion record
            db.session.execute(
                user_tests.update().where(
                    user_tests.c.user_id == current_user.id,
                    user_tests.c.test_id == test.id,
                    user_tests.c.completed_at == None
                ).values({
                    'completed_at': datetime.utcnow(),
                    'score': percentage_score,
                    'time_spent': time_spent
                })
            )
            
            db.session.commit()
            
            flash('Test submitted successfully!', 'success')
            return redirect(url_for('candidate_dashboard'))
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error submitting test: {str(e)}")
            flash('Error submitting test. Please try again.', 'error')
            return redirect(url_for('take_test', test_id=test_id))

    @app.route('/api/preview-code', methods=['POST'])
    @login_required
    def preview_code():
        if not current_user.is_admin:
            return jsonify({'error': 'Unauthorized'}), 403
        
        try:
            data = request.json
            code_text = data.get('code_text', '')
            language = data.get('language', 'c')
            
            lexer = get_lexer_by_name(language)
            formatter = HtmlFormatter(
                style='monokai',
                linenos=True,
                cssclass='highlight',
                linenostart=1
            )
            return highlight(code_text.strip(), lexer, formatter)
        except Exception as e:
            return str(e), 500

    # Helper functions
    def calculate_average_score(candidate):
        test_records = db.session.query(user_tests).filter_by(user_id=candidate.id).all()
        if not test_records:
            return 0
        scores = [record.score for record in test_records if record.score is not None]
        return sum(scores) / len(scores) if scores else 0

    def get_candidate_status(candidate):
        test_record = db.session.query(user_tests).filter_by(user_id=candidate.id).first()
        if not test_record:
            return 'Pending'
        latest_test = db.session.query(user_tests).filter_by(user_id=candidate.id)\
            .order_by(user_tests.c.started_at.desc()).first()
        if latest_test and latest_test.completed_at:
            return 'Completed'
        return 'Active'

    def get_completion_trend(start_date, end_date):
        # Implement actual data gathering
        return {
            'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'data': [75, 78, 82, 80, 85, 83, 85.7]
        }

    def get_score_distribution():
        # Implement actual data gathering
        return {
            'labels': ['90-100%', '80-89%', '70-79%', '60-69%', 'Below 60%'],
            'data': [10, 15, 20, 12, 8]
        }

    def get_category_performance():
        # Implement actual data gathering
        return {
            'labels': ['Basic Programming', 'OOP', 'Data Structures', 'Algorithms', 'Web Dev'],
            'data': [85, 78, 72, 68, 82]
        }

    def get_challenging_questions():
        # Implement actual data gathering
        return [
            {
                'question': 'What is polymorphism?',
                'category': 'OOP',
                'success_rate': '45%',
                'avg_time': '2.5 min'
            },
            # Add more questions...
        ]

    @app.route('/admin/questions/<int:question_id>/delete', methods=['POST'])
    @admin_required
    def delete_question(question_id):
        try:
            question = InterviewQuestion.query.get_or_404(question_id)
            
            # First remove the question from any tests it's in
            for test in Test.query.all():
                if question in test.questions:
                    test.questions.remove(question)
            
            # Then delete the question
            db.session.delete(question)
            db.session.commit()
            print(f"Successfully deleted question {question_id}")
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting question: {str(e)}")
            print(f"Full error: {str(e.__class__.__name__)}: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/admin/questions/<int:question_id>/edit', methods=['GET', 'POST'])
    @admin_required
    def edit_question(question_id):
        question = InterviewQuestion.query.get_or_404(question_id)
        
        if request.method == 'POST':
            try:
                question.category = request.form['category']
                question.question_text = request.form['question_text']
                question.code_text = request.form.get('code_text', '').strip()
                question.code_language = request.form.get('code_language', 'c')
                question.option_a = request.form['option_a']
                question.option_b = request.form['option_b']
                question.option_c = request.form['option_c']
                question.option_d = request.form['option_d']
                question.correct_answer = request.form['correct_answer'].upper()
                question.explanation = request.form['explanation']
                
                db.session.commit()
                flash('Question updated successfully!')
                return redirect(url_for('admin_questions'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error updating question: {str(e)}')
                return redirect(url_for('edit_question', question_id=question_id))
        
        return render_template('admin/edit_question.html', question=question)

    @app.route('/admin/tests')
    @admin_required
    def admin_tests():
        tests = Test.query.order_by(Test.id.desc()).all()
        
        # Calculate statistics for each test
        for test in tests:
            # Get all attempts for this test
            test_records = db.session.query(user_tests).filter_by(test_id=test.id).all()
            test.attempts = len(test_records)
            
            # Calculate average score
            scores = [record.score for record in test_records if record.score is not None]
            test.average_score = sum(scores) / len(scores) if scores else 0
        
        return render_template('admin/tests.html', tests=tests)

    @app.route('/admin/test/<int:test_id>/delete', methods=['POST'])
    @admin_required
    def delete_test(test_id):
        try:
            test = Test.query.get_or_404(test_id)
            
            # Delete test records
            db.session.execute(
                user_tests.delete().where(user_tests.c.test_id == test_id)
            )
            
            # Delete test
            db.session.delete(test)
            db.session.commit()
            
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/admin/test/edit/<int:test_id>', methods=['GET', 'POST'])
    @admin_required
    def admin_test_edit(test_id):
        test = Test.query.get_or_404(test_id)
        
        if request.method == 'POST':
            try:
                test.title = request.form['title']
                test.description = request.form['description']
                test.duration = int(request.form['duration'])
                test.passing_score = int(request.form['passing_score'])
                test.max_attempts = int(request.form['max_attempts'])
                
                # Update test questions
                selected_questions = request.form.getlist('selected_questions')
                # Remove old questions
                for question in test.questions:
                    db.session.delete(question)
                
                # Add new questions
                for question_id in selected_questions:
                    question = InterviewQuestion.query.get(int(question_id))
                    if question:
                        test_question = Question(
                            test_id=test.id,
                            question_text=question.question_text,
                            option_a=question.option_a,
                            option_b=question.option_b,
                            option_c=question.option_c,
                            option_d=question.option_d,
                            correct_answer=question.correct_answer,
                            explanation=question.explanation,
                            code_text=question.code_text,
                            code_language=question.code_language
                        )
                        db.session.add(test_question)
                
                db.session.commit()
                flash('Test updated successfully!')
                return redirect(url_for('admin_tests'))
                
            except Exception as e:
                db.session.rollback()
                flash(f'Error updating test: {str(e)}')
                return redirect(url_for('admin_test_edit', test_id=test_id))
        
        # Get all questions for selection
        questions = InterviewQuestion.query.all()
        return render_template('admin/edit_test.html', test=test, questions=questions)

    @app.route('/admin/candidate/<int:user_id>')
    @admin_required
    def view_candidate_details(user_id):
        candidate = User.query.get_or_404(user_id)
        if candidate.is_admin:
            abort(404)
        
        # Get test history before rendering template
        history = candidate.get_test_history()
        
        return render_template('admin/candidate_details.html', 
                             candidate=candidate,
                             history=history)

    @app.route('/candidate/test/<int:test_id>/start')
    @login_required
    def start_test(test_id):
        if current_user.is_admin:
            abort(403)
        
        test = Test.query.get_or_404(test_id)
        
        # Check for existing incomplete attempt
        existing_attempt = db.session.query(user_tests).filter(
            user_tests.c.user_id == current_user.id,
            user_tests.c.test_id == test.id,
            user_tests.c.completed_at == None
        ).first()
        
        if existing_attempt:
            # Delete the incomplete attempt
            db.session.execute(
                user_tests.delete().where(
                    user_tests.c.user_id == current_user.id,
                    user_tests.c.test_id == test.id,
                    user_tests.c.completed_at == None
                )
            )
            db.session.commit()
        
        # Create test record
        stmt = user_tests.insert().values(
            user_id=current_user.id,
            test_id=test.id,
            started_at=datetime.utcnow(),
            completed_at=None,
            score=None
        )
        db.session.execute(stmt)
        db.session.commit()
        
        return render_template('candidate/test.html', test=test)

    @app.route('/candidate/add-test', methods=['POST'])
    @login_required
    def add_test_access():
        if current_user.is_admin:
            return redirect(url_for('admin_dashboard'))
            
        test_code = request.form.get('test_code')
        if not test_code:
            flash('Please enter a test code', 'error')
            return redirect(url_for('candidate_dashboard'))
            
        test = Test.query.filter_by(test_code=test_code.upper()).first()
        if not test:
            flash('Invalid test code', 'error')
            return redirect(url_for('candidate_dashboard'))
            
        # Check if user already has access to this test
        if test in current_user.taken_tests:
            flash('You already have access to this test', 'info')
            return redirect(url_for('candidate_dashboard'))
            
        # Add test access for the user
        current_user.taken_tests.append(test)
        db.session.commit()
        
        flash('Test added successfully!', 'success')
        return redirect(url_for('candidate_dashboard'))

    @app.route('/candidate/test/<int:test_id>/progress', methods=['POST'])
    @login_required
    def save_test_progress(test_id):
        if current_user.is_admin:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        time_spent = data.get('time_spent', 0)
        security_logs = data.get('security_logs', [])
        
        # Update test progress
        test_record = db.session.query(user_tests).filter_by(
            user_id=current_user.id,
            test_id=test_id,
            completed_at=None
        ).first()
        
        if test_record:
            # Log security events
            for log in security_logs:
                test_log = TestLog(
                    user_id=current_user.id,
                    test_id=test_id,
                    event_type='security_event',
                    event_data=log
                )
                db.session.add(test_log)
            
            # Update time spent
            db.session.execute(
                user_tests.update().where(
                    user_tests.c.user_id == current_user.id,
                    user_tests.c.test_id == test_id,
                    user_tests.c.completed_at == None
                ).values(
                    time_spent=time_spent
                )
            )
            db.session.commit()
        
        return jsonify({'success': True})

    @app.route('/admin/test-result/<int:user_id>/<int:test_id>')
    @admin_required
    def view_test_result(user_id, test_id):
        candidate = User.query.get_or_404(user_id)
        test = Test.query.get_or_404(test_id)
        
        # Get test attempt record
        test_record = db.session.query(
            user_tests.c.score.label('score'),
            user_tests.c.completed_at.label('completed_at'),
            user_tests.c.time_spent.label('time_spent')
        ).filter(
            user_tests.c.user_id == user_id,
            user_tests.c.test_id == test_id,
            user_tests.c.completed_at != None
        ).first()
        
        if not test_record:
            flash('Test result not found', 'error')
            return redirect(url_for('admin_dashboard'))
        
        # Get all answers with their correctness
        answers = {}
        test_answers = TestAnswer.query.filter_by(
            user_id=user_id,
            test_id=test_id
        ).all()
        
        for answer in test_answers:
            answers[answer.question_id] = answer
        
        # Format time spent
        minutes = test_record.time_spent // 60
        seconds = test_record.time_spent % 60
        time_spent_formatted = f"{minutes}m {seconds}s"
        
        return render_template('admin/test_result.html',
                              candidate=candidate,
                              test=test,
                              questions=test.questions,
                              answers=answers,
                              score=test_record.score,
                              time_spent_formatted=time_spent_formatted)

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
        
        # Create admin if not exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', is_admin=True)
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()  # Commit admin user first to get ID
            
        # Create a sample test if no tests exist
        if not Test.query.first():
            # First create some questions
            question1 = InterviewQuestion(
                category="Basic Programming",
                question_text="What is a variable?",
                option_a="A container for data",
                option_b="A loop construct",
                option_c="A function name",
                option_d="A class definition",
                correct_answer="A",
                explanation="A variable is a named container that stores data in programming."
            )
            
            question2 = InterviewQuestion(
                category="Basic Programming",
                question_text="What is a function?",
                option_a="A data type",
                option_b="A reusable block of code",
                option_c="A variable name",
                option_d="A loop statement",
                correct_answer="B",
                explanation="A function is a reusable block of code that performs a specific task."
            )
            
            # Add a question with code
            question3 = InterviewQuestion(
                category="C Programming",
                question_text="How many times is i checked in the following program?",
                code_text="""
                #include <stdio.h>
                int main() {
                    int i;
                    for(i=0; i<3; i++) {
                        printf("%d\\n", i);
                    }
                    return 0;
                }
                """,
                code_language="c",
                option_a="2",
                option_b="3",
                option_c="4",
                option_d="1",
                correct_answer="C",
                explanation="The condition i < 3 is checked 4 times: initially (i=0), after i=1, after i=2, and finally after i=3 when the loop terminates"
            )
            
            db.session.add(question1)
            db.session.add(question2)
            db.session.add(question3)
            db.session.commit()
            
            # Get admin ID after commit
            admin = User.query.filter_by(username='admin').first()
            
            # Create a test with these questions
            test = Test(
                title="Basic Programming Test",
                description="Test your basic programming knowledge",
                duration=1,  # 1 minute
                passing_score=1,  # 1%
                max_attempts=1,
                created_by=admin.id,
                test_code=Test.generate_test_code()
            )
            
            db.session.add(test)
            db.session.commit()
            
            # Create Question instances
            test_q1 = Question(
                test_id=test.id,
                question_text=question1.question_text,
                option_a=question1.option_a,
                option_b=question1.option_b,
                option_c=question1.option_c,
                option_d=question1.option_d,
                correct_answer=question1.correct_answer,
                explanation=question1.explanation
            )
            test_q2 = Question(
                test_id=test.id,
                question_text=question2.question_text,
                option_a=question2.option_a,
                option_b=question2.option_b,
                option_c=question2.option_c,
                option_d=question2.option_d,
                correct_answer=question2.correct_answer,
                explanation=question2.explanation
            )
            test_q3 = Question(
                test_id=test.id,
                question_text=question3.question_text,
                option_a=question3.option_a,
                option_b=question3.option_b,
                option_c=question3.option_c,
                option_d=question3.option_d,
                correct_answer=question3.correct_answer,
                explanation=question3.explanation,
                code_text=question3.code_text,
                code_language=question3.code_language
            )
            
            db.session.add(test_q1)
            db.session.add(test_q2)
            db.session.add(test_q3)
            db.session.commit()
            
            print(f"Created sample test (ID: {test.id}) with {len(test.questions)} questions")
            
        # Add a sample question with code
        sample_question = InterviewQuestion(
            category="C Programming",
            question_text="How many times will this loop execute?",
            code_text="""#include <stdio.h>
int main() {
    int i;
    for(i=1; i<=5; i++) {
        printf("%d\\n", i);
    }
    return 0;
}""",
            code_language="c",
            option_a="2",
            option_b="5",
            option_c="4",
            option_d="None of these",
            correct_answer="B",
            explanation="The loop will execute 5 times, printing values from 1 to 5"
        )

        db.session.add(sample_question)
        db.session.commit()
        
    #app.run(debug=True) 