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

# Promt to run collectstatic
$collectstatic = Read-Host "Do you want to run 'python manage.py collectstatic'? (yes/no)"
if ($collectstatic -eq "yes") {
    python manage.py collectstatic
}

# Run the server
python manage.py runserver