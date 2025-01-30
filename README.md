# HERMES

## **H**igh **E**fficiency **R**ecording and **M**anagement **E**valuation **S**ystem

A website to help my dance club manage the results of the physical testings done every year. The website is using Django fully, with dynamic features done by unicorn. I've setup an account for you.

username: `hacker` password: `hackclub`

Try out creating a new profile and addidg some test result to it. You are welcome to try to break the site (I want to see if it holds up :D).

## Prerequisites

- Python installed
- PostgreSQL installed
- Git (so you can clone the repo)

## Steps to Set Up the Project

### 1. Clone the Repository

```bash
git clone https://github.com/DaalbuCZ/Hermes.git
cd hermes
```

### 2. Set Up the Virtual Environment

```bash
python -m venv myenv
source myenv/bin/activate  # On macOS/Linux
myenv\Scripts\activate.bat  # On Windows
```

### 3. Install Requirements

Install the required packages:

```bash
pip install -r requirements.txt
```

### 4. Configure Database Settings

Edit `hermes/settings.py` to ensure the database settings are correct for the target machine.

### 5. Migrate the Database

Run migrations:

```bash
python manage.py migrate
```

### 6. Create a Superuser

Create a superuser:

```bash
python manage.py createsuperuser
```

### 7. Start the Development Server

Start the Django development server:

```bash
python manage.py runserver
```

### 8. Access the Site

Access your site at `http://localhost:8000`
and admin dashboard at `http://localhost:8000/admin`
