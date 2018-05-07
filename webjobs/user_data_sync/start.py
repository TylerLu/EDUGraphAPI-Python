import constants
from models import database
from user_data_sync_service import UserDataSyncService


database.connect()

user_data_sync_service = UserDataSyncService()
user_data_sync_service.sync()

database.close()