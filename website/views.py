from flask import Blueprint, redirect, render_template, request, flash, jsonify, url_for
from flask_login import login_required, current_user
from .models import Note, QuizAnswer, QuizScore
from . import db
import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')#Gets the note from the HTML 

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)  #providing the schema for the note 
            db.session.add(new_note) #adding the note to the database 
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user, )


@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})

@views.route('/quiz', methods=['GET', 'POST'])
@login_required
def quiz():
    if request.method == 'POST':
        username = request.form.get('username')

        # Save quiz answers to the database
        for question_number in range(1, 7):
            answer = request.form.get(f'question{question_number}')
            quiz_answer = QuizAnswer(user_id=current_user.id, question_number=question_number, answer=answer)
            db.session.add(quiz_answer)

        # Calculate score (example: count correct answers)
        correct_answers = QuizAnswer.query.filter_by(user_id=current_user.id, answer='correct_answer').count()
        total_questions = 6
        score = int((correct_answers / total_questions) * 100)

        # Save quiz score to the database
        quiz_score = QuizScore(user_id=current_user.id, score=score)
        db.session.add(quiz_score)

        db.session.commit()
        flash('Quiz answers submitted successfully!', category='success')

        # Redirect to a page displaying the score
        return redirect(url_for('views.quiz_result', score=score, username=username))

    return render_template("quiz.html", user=current_user)

@views.route('/quiz/result/<int:score>/<username>')
@login_required
def quiz_result(score, username):
    return render_template("quiz_result.html", user=current_user, score=score, username=username)


@views.route('/leaderboard')
def show_leaderboard():
    # Data hardcoded untuk ditampilkan di tabel
    test_scores = [
        {'name': 'Testing 1', 'score': 80},
        {'name': 'Testing 2', 'score': 95},
        {'name': 'Testing 3', 'score': 75},
        {'name': 'Testing 4', 'score': 88},
        {'name': 'Testing 5', 'score': 92},
        {'name': 'Testing 6', 'score': 78},
        {'name': 'Testing 7', 'score': 89},
        {'name': 'Testing 8', 'score': 96},
        {'name': 'Testing 9', 'score': 85},
        {'name': 'Testing 10', 'score': 91},
    ]

    return render_template('leaderboard.html', test_scores=test_scores)


