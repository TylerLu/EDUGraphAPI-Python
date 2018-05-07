import os

client_id = os.environ['ClientId']
client_cert_path = os.environ['ClientCertificatePath']
client_cert_password = os.environ['ClientCertificatePassword']

aad_instance = 'https://login.microsoftonline.com/'
ms_graph_resource = 'https://graph.microsoft.com'