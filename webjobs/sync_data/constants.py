'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''

import os

client_id = os.environ['ClientId']
client_cert_path = os.environ['ClientCertificatePath']
client_cert_password = os.environ['ClientCertificatePassword']

aad_instance = 'https://login.microsoftonline.com/'
ms_graph_resource = 'https://graph.microsoft.com'

mysql_host = os.environ['MySQLHost']
mysql_port = 3306
mysql_name = 'edu'
mysql_user = os.environ['MySQLUser']
mysql_password = os.environ['MySQLPassword']