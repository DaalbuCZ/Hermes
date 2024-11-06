class TestResultDatabaseRouter:
    def db_for_read(self, model, **hints):
        return self.get_db(model)

    def db_for_write(self, model, **hints):
        return self.get_db(model)

    def get_db(self, model):
        from .models import TestResultDatabase

        # Bypass the router for TestResultDatabase model
        if model == TestResultDatabase:
            return "default"

        # Logic to get the selected database, e.g., from session or a global setting
        selected_db = TestResultDatabase.objects.using(
            "default"
        ).first()  # Example: get the first database
        if selected_db:
            return selected_db.name
        return "default"
