import bcrypt
import getpass

print("=== GENERADOR DE HASH SEGURO ===")
print()

# Pedir contraseña sin mostrarla
password = getpass.getpass("Escribe la contraseña: ")
password_confirm = getpass.getpass("Confirma la contraseña: ")

if password != password_confirm:
    print("❌ Las contraseñas no coinciden")
else:
    # Generar hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    print("\n" + "="*50)
    print("✅ HASH GENERADO:")
    print("="*50)
    print(f"\nPega esto en tu config.yaml:")
    print(f"password: {hashed.decode('utf-8')}")
    print(f"\nEl usuario usará esta contraseña: '{password}'")
    print("="*50)
