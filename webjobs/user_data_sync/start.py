import os
import adal
from OpenSSL import crypto
from cryptography.hazmat.primitives import serialization


client_id = os.environ['ClientId']
client_cert_path = os.environ['ClientCertificatePath']
client_cert_password = os.environ['ClientCertificatePassword']

aad_instance = 'https://login.microsoftonline.com/'
ms_graph_resource = 'https://graph.microsoft.com'

# load certificate and thumbprint
with open(client_cert_path, 'rb') as cert_file:
    pkcs12 = crypto.load_pkcs12(cert_file.read(), client_cert_password)

private_key = pkcs12.get_privatekey() \
    .to_cryptography_key()  \
    .private_bytes(
        serialization.Encoding.PEM, 
        serialization.PrivateFormat.PKCS8, 
        serialization.NoEncryption())

thumbprint = pkcs12.get_certificate() \
    .digest('sha1') \
    .decode() \
    .replace(':', '')

# get access token
tenant_id = '64446b5c-6d85-4d16-9ff2-94eddc0c2439'
authority = aad_instance + tenant_id
auth_context = adal.AuthenticationContext(authority)

import pdb; pdb.set_trace()
token = auth_context.acquire_token_with_client_certificate(
    ms_graph_resource,
    client_id,
    private_key,
    thumbprint)

print(token['accessToken'])