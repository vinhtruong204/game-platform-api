import enum


class AuthProvider(str, enum.Enum):
    google = "google"
    apple = "apple"
    guest = "guest"
    dev = "dev"
