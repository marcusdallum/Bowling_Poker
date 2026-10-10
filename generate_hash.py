from werkzeug.security import generate_password_hash
import getpass

password = getpass.getpass("Enter your desired admin password: ")
hashed = generate_password_hash(password)
print(f"\nYour secure password hash is:\n{hashed}\n\nCopy this string into your .env file as ADMIN_PASSWORD_HASH.")
