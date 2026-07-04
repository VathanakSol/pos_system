class User:
    ROLES = ("cashier", "manager")

    def __init__(self, username, password, role):
        if role not in self.ROLES:
            raise ValueError(f"Invalid role '{role}'. Must be one of {self.ROLES}")
        self.username = username
        self.password = password  # stored as plain text (demo only)
        self.role = role

    def is_manager(self):
        return self.role == "manager"

    def __repr__(self):
        return f"{self.username} ({self.role})"
