# Navigate to the hermes directory
Set-Location -Path "hermes"

# Prompt to run makemigrations
$makemigrations = Read-Host "Do you want to run 'python manage.py makemigrations'? (yes/no)"
if ($makemigrations -eq "yes") {
    python manage.py makemigrations
}

# Prompt to run migrate
$migrate = Read-Host "Do you want to run 'python manage.py migrate'? (yes/no)"
if ($migrate -eq "yes") {
    python manage.py migrate
}

# Run the server
python manage.py runserver