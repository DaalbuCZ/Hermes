from django.db import models


class TestResultDatabase(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


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

        # Logic to get the selected database from session
        selected_db = self.get_selected_db()
        if selected_db:
            return selected_db
        return "default"

    def get_selected_db(self):
        from django.conf import settings
        from django.utils.deprecation import MiddlewareMixin

        class DatabaseMiddleware(MiddlewareMixin):
            def process_request(self, request):
                return request.session.get("selected_db", "default")

        return DatabaseMiddleware().process_request(None)
