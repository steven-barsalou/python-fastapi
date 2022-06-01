from pydantic import BaseSettings

#a class creating from the pydantic library that will create your environment variables and validate their types in, case insensitive when it comes to variable and environment variable names
class Settings(BaseSettings):
    #database_password: str = "localhost" #if there is no default, the Settings class will throw an error when this variable is missing
    database_hostname: str
    database_port: str
    database_name: str
    database_username: str
    database_password: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    class Config: #this will pull in the .env file settings
        env_file = ".env"

settings = Settings() #get the settings by instantiation the Settings class
#print(settings.secret_key) #print the values of one of the keys

#example of how to get an environment variable
#import os #to get an environment variable
#processors = os.getenv("NUMBER_OF_PROCESSORS")