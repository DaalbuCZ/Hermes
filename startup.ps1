# Activate the virtual environment
.\olympvenv\Scripts\Activate.ps1

# Navigate to the hermes directory
Set-Location -Path "hermes"

# Prompt to run makemigrations
$makemigrations = Read-Host "Do you want to run 'python manage.py makemigrations'? (y/n)"
if ($makemigrations -eq "y") {
    python manage.py makemigrations
}

# Prompt to run migrate
$migrate = Read-Host "Do you want to run 'python manage.py migrate'? (y/n)"
if ($migrate -eq "y") {
    python manage.py migrate
}

# Promt to run collectstatic
$collectstatic = Read-Host "Do you want to run 'python manage.py collectstatic'? (y/n)"
if ($collectstatic -eq "y") {
    python manage.py collectstatic
}

# Run the server
python manage.py runserver