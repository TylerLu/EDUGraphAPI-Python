
import adal
import constants

from OpenSSL import crypto
from cryptography.hazmat.primitives import serialization


class AuthenticationHelper(object):

    def __init__(self, cert_path, cert_password):
        self.__cert_private_key, self.__cert_thumbprint = \
            self._get_certificate_private_key_and_thumbnail(cert_path, cert_password)

    def get_app_only_access_token(self, tenant_id, client_id, resource):

        authority = constants.aad_instance + tenant_id
        auth_context = adal.AuthenticationContext(authority, api_version=None)

        token = auth_context.acquire_token_with_client_certificate(
            resource,
            client_id,
            self.__cert_private_key,
            self.__cert_thumbprint)
        
        return token['accessToken']

    def _get_certificate_private_key_and_thumbnail(self, cert_path, cert_password):

        with open(cert_path, 'rb') as cert_file:
            pkcs12 = crypto.load_pkcs12(cert_file.read(), cert_password)

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

        return private_key, thumbprint