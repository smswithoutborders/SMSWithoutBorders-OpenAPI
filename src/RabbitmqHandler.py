import logging
import pika
import json
import ssl
import requests

from settings import Configurations
rabbitmq_host = Configurations.RABBITMQ_HOST
rabbitmq_management_port = Configurations.RABBITMQ_MANAGEMENT_PORT
rabbitmq_server_port = Configurations.RABBITMQ_SERVER_PORT
rabbitmq_user = Configurations.RABBITMQ_USER
rabbitmq_password = Configurations.RABBITMQ_PASSWORD
rabbitmq_ssl_active = Configurations.RABBITMQ_SSL_ACTIVE
rabbitmq_ssl_host = Configurations.RABBITMQ_SSL_HOST
rabbitmq_ssl_port = Configurations.RABBITMQ_SSL_PORT
rabbitmq_ssl_cacert = Configurations.RABBITMQ_SSL_CACERT
rabbitmq_ssl_crt = Configurations.RABBITMQ_SSL_CRT
rabbitmq_ssl_key = Configurations.RABBITMQ_SSL_KEY
rabbitmq_exchange_name = Configurations.RABBITMQ_EXCHANGE_NAME
rabbitmq_exchange_type = Configurations.RABBITMQ_EXCHANGE_TYPE
rabbitmq_queue_name = Configurations.RABBITMQ_QUEUE_NAME
rabbitmq_url_protocol = "https" if rabbitmq_ssl_active else "http"

logging.basicConfig(level=logging.DEBUG)

class RabbitMQ:
    def __init__(self, dev_id: str):
        """ 
        """
        self.rabbitmq_req_url = f"{rabbitmq_url_protocol}://{rabbitmq_host}:{rabbitmq_management_port}"
        self.dev_id = dev_id
        self.__create_exchange_if_not_exist__(exchange_name=rabbitmq_exchange_name)

    def __create_exchange_if_not_exist__(self, exchange_name: str) -> None:
        """
        """
        get_exchange_url = f"{self.rabbitmq_req_url}/api/exchanges/%2F/{exchange_name}"
        get_exchange_response = requests.get(url=get_exchange_url, auth=(rabbitmq_user, rabbitmq_password))

        if get_exchange_response.status_code == 200:
            return None

        elif get_exchange_response.status_code == 404:
            add_exchange_url = f"{self.rabbitmq_req_url}/api/exchanges/%2F/{exchange_name}"
            add_exchange_data = {
                "type":"topic",
                "durable":True
            }
            add_exchange_response = requests.put(url=add_exchange_url, json=add_exchange_data, auth=(rabbitmq_user, rabbitmq_password))

            if add_exchange_response.status_code in [201, 204]:
                logging.debug("[*] New exchange added")
                return None

            else:
                logging.error("Failed to add exchange")
                add_exchange_response.raise_for_status()
            
        else:
            get_exchange_response.raise_for_status()

    def add_user(self, dev_key: str) -> None:
        """ 
        """
        if self.exist():
            logging.info("user %s already exist", self.dev_id)
        else:
            try:
                add_user_url = f"{self.rabbitmq_req_url}/api/users/{self.dev_id}"
                add_user_data = {
                    "password":dev_key,
                    "tags":"management"
                }
                add_user_response = requests.put(url=add_user_url, json=add_user_data, auth=(rabbitmq_user, rabbitmq_password))

                if add_user_response.status_code in [201, 204]:
                    logging.debug("[*] New user added")
                    logging.debug("[*] User tag set")

                    set_permissions_url = f"{self.rabbitmq_req_url}/api/permissions/%2F/{self.dev_id}"
                    set_permissions_data = {
                        "configure":f"^({rabbitmq_exchange_name}|{self.dev_id}_.*)$",
                        "write":f"^({rabbitmq_exchange_name}|{self.dev_id}_.*)$",
                        "read":f"^({rabbitmq_exchange_name}|{self.dev_id}_.*)$"
                    }
                    set_permissions_response = requests.put(url=set_permissions_url, json=set_permissions_data, auth=(rabbitmq_user, rabbitmq_password))

                    if set_permissions_response.status_code in [201, 204]:
                        logging.debug("[*] User privilege set")
                        return None

                    else:
                        logging.error("Failed to set user privilege")
                        set_permissions_response.raise_for_status()

                else:
                    logging.error("Failed to add new user")
                    add_user_response.raise_for_status()

            except Exception as error:
                raise error

    def delete(self) -> None:
        """
        """
        try:
            delete_user_url = f"{self.rabbitmq_req_url}/api/users/{self.dev_id}"
            delete_user_response = requests.delete(url=delete_user_url, json={}, auth=(rabbitmq_user, rabbitmq_password))

            if delete_user_response.status_code == 204:
                logging.debug("[*] User deleted")
                return None

            else:
                delete_user_response.raise_for_status()

        except Exception as error:
            raise error

    def exist(self) -> bool:
        """ 
        """
        try:
            url = f"{self.rabbitmq_req_url}/api/users/{self.dev_id}"
            response = requests.get(url=url, auth=(rabbitmq_user, rabbitmq_password))

            if response.status_code == 200:
                return True
            elif response.status_code == 404:
                return False
            else:
                response.raise_for_status()

        except Exception as error:
            raise error

    def request_sms(
        self,
        data: dict,
        rabbitmq_host_url: str = rabbitmq_host,
        rabbitmq_exchange_name: str = rabbitmq_exchange_name,
        rabbitmq_queue_name: str = rabbitmq_queue_name,
        rabbitmq_port: str = rabbitmq_server_port
    ) -> None:
        """ 
        """
        conn_params = None
        credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
        if rabbitmq_ssl_active:

            context = ssl.create_default_context(cafile=rabbitmq_ssl_cacert) 
            context.load_cert_chain(rabbitmq_ssl_crt, rabbitmq_ssl_key)

            ssl_options = pika.SSLOptions(context)
            logging.error("ssl connecting on: %s", rabbitmq_ssl_host)
            conn_params = pika.ConnectionParameters(
                    port=rabbitmq_ssl_port, 
                    ssl_options=ssl_options,
                    credentials=credentials
                )
        else:
            conn_params = pika.ConnectionParameters( 
                    host=rabbitmq_host_url, 
                    port=rabbitmq_port,
                    credentials=credentials
                )

        connection = pika.BlockingConnection(
                conn_params
        )
        channel = connection.channel()

        if not "operator_name" in data:
            raise Exception("Missing operator name")

        if not "text" in data:
            raise Exception("Missing text in data")

        if not "number" in data:
            raise Exception("Missing number in data")

        operator_name = data["operator_name"]
        routing_key = "%s_%s.%s" % (self.dev_id, rabbitmq_queue_name, operator_name)

        text = data["text"]
        number = data["number"]
        data = json.dumps({"text": text, "number": number})

        try:
            channel.basic_publish(
                exchange=rabbitmq_exchange_name,
                routing_key=routing_key,
                body=data,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                ),
            )
        except Exception as error:
            raise error