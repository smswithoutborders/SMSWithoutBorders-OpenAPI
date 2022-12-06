import os

MODE = os.environ.get("MODE")

if MODE and MODE.lower() == "production":
    class production:
        SSL_PORT = os.environ["SSL_PORT"]
        SSL_CERTIFICATE = os.environ["SSL_CERTIFICATE"]
        SSL_KEY = os.environ["SSL_KEY"]
        SSL_PEM = os.environ["SSL_PEM"]

    baseConfig = production

else:
    class development:
        SSL_PORT = os.environ.get("SSL_PORT") 
        SSL_CERTIFICATE = os.environ.get("SSL_CERTIFICATE") or "" 
        SSL_KEY = os.environ.get("SSL_KEY") or "" 
        SSL_PEM = os.environ.get("SSL_PEM") or "" 
    
    baseConfig = development

class Configurations(baseConfig):
    MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE")
    MYSQL_HOST = os.environ.get("MYSQL_HOST")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD")
    MYSQL_USER = os.environ.get("MYSQL_USER")

    HOST = os.environ.get("HOST")
    PORT = os.environ.get("PORT")

    DEV_HOST = os.environ.get("DEV_HOST")
    DEV_PORT = os.environ.get("DEV_PORT")
    DEV_VERSION = os.environ.get("DEV_VERSION")
    DEV_COOKIE_NAME = "SWOBDev"

    ID = os.environ.get("ID")
    KEY = os.environ.get("KEY")

    RABBITMQ_USER = os.environ.get("RABBITMQ_USER") or "guest"
    RABBITMQ_PASSWORD = os.environ.get("RABBITMQ_PASSWORD") or "guest"
    RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST") or "127.0.0.1"
    RABBITMQ_MANAGEMENT_PORT = os.environ.get("RABBITMQ_MANAGEMENT_PORT") or "15672"
    RABBITMQ_SERVER_PORT = os.environ.get("RABBITMQ_SERVER_PORT") or "5672"
    RABBITMQ_EXCHANGE_NAME = os.environ.get("RABBITMQ_EXCHANGE_NAME") or "DEKU_CLUSTER_SMS"
    RABBITMQ_EXCHANGE_TYPE = os.environ.get("RABBITMQ_EXCHANGE_TYPE") or "topic"
    RABBITMQ_QUEUE_NAME = os.environ.get("RABBITMQ_QUEUE_NAME") or "OUTGOING_SMS"

    RABBITMQ_SSL_ACTIVE = False if (os.environ.get("RABBITMQ_SSL_ACTIVE") or "False").lower() == "false" else True if (os.environ.get("RABBITMQ_SSL_ACTIVE") or "False").lower() == "true" else False
    RABBITMQ_SSL_HOST = os.environ.get("RABBITMQ_SSL_HOST") 
    RABBITMQ_MANAGEMENT_PORT_SSL = os.environ.get("RABBITMQ_MANAGEMENT_PORT_SSL") or "15671"
    RABBITMQ_SERVER_PORT_SSL = os.environ.get("RABBITMQ_SERVER_PORT_SSL") or "5671"
    RABBITMQ_SSL_CACERT = os.environ.get("RABBITMQ_SSL_CACERT") or ""
    RABBITMQ_SSL_CRT = os.environ.get("RABBITMQ_SSL_CRT") or ""
    RABBITMQ_SSL_KEY = os.environ.get("RABBITMQ_SSL_KEY") or ""