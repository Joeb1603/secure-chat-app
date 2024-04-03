from werkzeug.security import check_password_hash

class User:

    def __init__(self, user_data):
        self.username = user_data['_id']
        self.password = user_data['password']
        self.browser_fingerprint = user_data['browser_fingerprint']
        self.current_room = user_data['current_room']

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username

    def get_current_room(self):
        return self.current_room

    def validate_fingerprint(self, fingerprint):
        print(f"{fingerprint} == {self.browser_fingerprint}")
        return True if fingerprint == self.browser_fingerprint else False

    def password_correct(self, password_to_check):
        return check_password_hash(self.password, password_to_check)
