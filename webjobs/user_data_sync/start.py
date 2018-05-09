'''
 *   * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 *   * See LICENSE in the project root for license information.
'''

import sys
import constants
from models import database
from user_data_sync_service import UserDataSyncService

def main():
    try:
        database.connect()
        user_data_sync_service = UserDataSyncService()
        user_data_sync_service.sync()
    except:
        print("Unexpected error: ", sys.exc_info()[0])
    finally:
        database.close()

if __name__ == "__main__":
    main()