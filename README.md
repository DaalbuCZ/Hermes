# HERMES
## **H**igh **E**fficiency **R**ecording and **M**anagement **E**valuation **S**ystem


## Prerequisites

- Python installed
- PostgreSQL installed
- Git (if cloning from a repository)
- Basic understanding of Django and Python

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

## Additional Considerations

- Check if any environment-specific settings need to be adjusted.

