import bcrypt

def create_hash(text: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(text.encode(), salt).decode()

def verify_hash(plain_hash: str, hashed_hash: str) -> bool:
    return bcrypt.checkpw(plain_hash.encode(), hashed_hash.encode())