import sqlite3

conn = sqlite3.connect('dnd.db')
c = conn.cursor()

# Create table
c.execute('''CREATE TABLE questions
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              question TEXT NOT NULL,
              answer TEXT NOT NULL)''')

# Insert sample data
sample_questions = [
    ("What is the capital of France?", "Paris"),
    ("What is 2 + 2?", "4"),
    ("Who wrote 'To Kill a Mockingbird'?", "Harper Lee"),
    ("What is the largest planet in our solar system?", "Jupiter"),
    ("In which year did the Titanic sink?", "1912"),
    ("What is the smallest country in the world?", "Vatican City"),
    ("Who painted the Mona Lisa?", "Leonardo da Vinci"),
    ("What is the hardest natural substance on Earth?", "Diamond"),
    ("Who developed the theory of relativity?", "Albert Einstein"),
    ("What is the capital of Japan?", "Tokyo")
]

c.executemany('INSERT INTO questions (question, answer) VALUES (?,?)', sample_questions)

# Save (commit) the changes
conn.commit()

# Close the connection
conn.close()
