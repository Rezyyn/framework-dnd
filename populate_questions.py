from app import app, db
from models import Question

with app.app_context():
    db.create_all()

    questions = [
        {"question": "What is the capital of France?", "answer": "Paris"},
        {"question": "What is 2 + 2?", "answer": "4"},
        {"question": "What is the color of the sky?", "answer": "Blue"}
    ]

    for q in questions:
        question = Question(question=q['question'], answer=q['answer'])
        db.session.add(question)

    db.session.commit()
