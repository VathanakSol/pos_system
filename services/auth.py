import json
import os

from models.user import User

USERS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "users.json")


class AuthService:
    def __init__(self):
        self._users = {}
        self._load()

    def _load(self):
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r") as f:
                for d in json.load(f):
                    u = User(d["username"], d["password"], d["role"])
                    self._users[u.username] = u
        else:
            self._seed()
            self._save()

    def _seed(self):
        defaults = [
            User("admin",   "admin123", "manager"),
            User("cashier", "cash123",  "cashier"),
        ]
        for u in defaults:
            self._users[u.username] = u

    def _save(self):
        os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
        data = [
            {"username": u.username, "password": u.password, "role": u.role}
            for u in self._users.values()
        ]
        with open(USERS_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def login(self, username, password):
        """Return User if credentials match, else None."""
        user = self._users.get(username)
        if user and user.password == password:
            return user
        return None

    def add_user(self, username, password, role):
        if username in self._users:
            raise ValueError(f"Username '{username}' already exists")
        user = User(username, password, role)
        self._users[username] = user
        self._save()
        return user

    def get_all(self):
        return list(self._users.values())
