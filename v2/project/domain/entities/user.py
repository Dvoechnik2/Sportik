# domain/entities/user.py

class User:
    def __init__(self, user_id, name, phone=None):
        self.user_id = user_id
        self.name = name
        self.phone = phone
        self.is_verified = phone is not None
