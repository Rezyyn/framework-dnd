import os

# Directory path of the repository
repo_path = 'C:\\Users\\James\\Documents\\vscode_projects\\framework-dnd'
# List of files to read
files_to_read = [
    'README.md',
    'app.py',
    'db.py',
    'decorators.py',
    'forms.py',
    'init_db.py',
    'models.py',
    'package-lock.json',
    'package.json',
    'populate_questions.py',
    'profile.py',
    'requirements.txt',
    'views.py'
]

# Function to read and store the contents of files
file_contents = {}
for file_name in files_to_read:
    file_path = os.path.join(repo_path, file_name)
    if os.path.isfile(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                file_contents[file_name] = file.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as file:
                file_contents[file_name] = file.read()

# Write the contents to a new file for easier reading
output_file_path = 'C:\\Users\\James\\Documents\\vscode_projects\\framework-dnd\\framework_dnd_files_contents.txt'
with open(output_file_path, 'w', encoding='utf-8') as output_file:
    for file_name, content in file_contents.items():
        output_file.write(f'=== {file_name} ===\n')
        output_file.write(content)
        output_file.write('\n\n')

output_file_path
