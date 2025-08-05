# Prompt to run makemigrations
$makemigrations = Read-Host "Do you want to run 'python manage.py makemigrations'? (y/N)"
if ($makemigrations -eq "y") {
    python manage.py makemigrations
}

# Prompt to run migrate
$migrate = Read-Host "Do you want to run 'python manage.py migrate'? (y/N)"
if ($migrate -eq "y") {
    python manage.py migrate
}

# Promt to run collectstatic
$collectstatic = Read-Host "Do you want to run 'python manage.py collectstatic'? (y/N)"
if ($collectstatic -eq "y") {
    python manage.py collectstatic
}

# Prompt to run local server
$local = Read-Host "Do you want to run 'python manage.py runserver locally'? (Y/n)"
if ($local -eq "n") {
    python manage.py runserver 192.168.0.150:8000
} else {
    python manage.py runserver
}
