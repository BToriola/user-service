# Note: Firestore is schemaless, but we define a model for clarity
class UserProfile:
    def __init__(self, email, subscription_status="free", preferences=None):
        self.email = email
        self.subscription_status = subscription_status
        self.preferences = preferences or {"modification_mode": "suggestion"}

    def to_dict(self):
        return {
            "email": self.email,
            "subscription_status": self.subscription_status,
            "preferences": self.preferences
        }