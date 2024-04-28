import ssl
import socket
from OpenSSL import crypto

def obtener_certificado_y_clave_privada(url, puerto, nombre_archivo_certificado, nombre_archivo_clave):
    # Establecer una conexión SSL con el sitio web
    context = ssl.create_default_context()
    with socket.create_connection((url, puerto)) as sock:
        with context.wrap_socket(sock, server_hostname=url) as ssock:
            # Obtener el certificado del sitio web
            certificado = ssl.DER_cert_to_PEM_cert(ssock.getpeercert(True))
            # Guardar el certificado en un archivo
            with open(nombre_archivo_certificado, "w") as archivo_certificado:
                archivo_certificado.write(certificado)
            # Obtener la clave privada del sitio web (esto puede no ser posible)
            try:
                clave_privada = ssock.getpeercert(True)
                with open(nombre_archivo_clave, "w") as archivo_clave:
                    archivo_clave.write(str(clave_privada))
            except ssl.SSLError:
                print("No se pudo obtener la clave privada del servidor.")

# URL y puerto del sitio web del que quieres obtener el certificado y la clave privada
url = 'www.python.org'
puerto = 443

# Nombre del archivo donde se guardará el certificado
nombre_archivo_certificado = 'certificado_python_org.pem'

# Nombre del archivo donde se guardará la clave privada
nombre_archivo_clave = 'clave_privada_python_org.pem'

# Obtener el certificado SSL y la clave privada y guardarlos en archivos
obtener_certificado_y_clave_privada(url, puerto, nombre_archivo_certificado, nombre_archivo_clave)
print("Certificado y clave privada guardados.")


# Generar una clave privada de tipo RSA de 2048 bits
key = crypto.PKey()
key.generate_key(crypto.TYPE_RSA, 2048)

# Crear una solicitud de certificado
req = crypto.X509Req()
req.get_subject().CN = "myapp.com"
req.set_pubkey(key)
req.sign(key, "sha256")

# Crear un certificado autofirmado
cert = crypto.X509()
cert.set_serial_number(0)
cert.gmtime_adj_notBefore(0)
cert.gmtime_adj_notAfter(10*365*24*60*60)  # Valido por 10 años
cert.set_issuer(req.get_subject())
cert.set_subject(req.get_subject())
cert.set_pubkey(req.get_pubkey())
cert.sign(key, "sha256")

# Guardar la clave privada y el certificado en archivos
with open("myapp.key", "wt") as f:
    f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key).decode("utf-8"))
with open("myapp.crt", "wt") as f:
    f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode("utf-8"))
