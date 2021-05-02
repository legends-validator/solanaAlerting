import json
import requests
from time import sleep
import datetime
import logging


logging.getLogger().setLevel(logging.INFO)


def twillio_notification(twillio_api_token, phone_list, twillio_url, origin_number, message):
    time = datetime.datetime.utcnow().strftime("%a %b %d %H:%M:%S %Z %Y")
    headers = {
        "Authorization": "Basic {twillio_api_token}".format(twillio_api_token=twillio_api_token),
        "Content-Type": "application/x-www-form-urlencoded",
    }
    try:
        for i in phone_list:
            payload = (
                "To=%2B{i}&From=%2B{origin_number}&Body=Solana%20{message}%20{time}".format(
                    i=i, origin_number=origin_number, message=message, time=time
                )
            )
            requests.request("POST", twillio_url, headers=headers, data=payload)
    except Exception as e:
        logging.info("Twillio notifcation failed")
        logging.info("e".format(e=e))
        return


def solana_rpc(rpc_url):
    headers = {"Content-Type": "application/json"}
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "getHealth"})
    try:
        response = requests.request("POST", rpc_url, headers=headers, data=payload)
        response = response.json()

        try:
            message = response["result"]
            return message
        except KeyError:
            message = response["error"]["message"]
            return message
    except Exception as e:
        logging.info("Failed to retrieve health RPC call from Solana Node")
        logging.info("e".format(e=e))
        message = "Solana Node unreachable"
        return message


if __name__ == "__main__":
    while True:
        with open("vars.json", "r") as f:
            f = json.load(f)
            rpc_url = f["rpc_url"]
            message = solana_rpc(rpc_url)
            #message = "Test Message. Nothing to worry about."
            if message == "ok":
                logging.info(
                    "Status is {message}, sleeping for 60 seconds".format(message=message)
                )
                sleep(60)
                continue
            logging.info(message)
            twillio_api_token = f["twillio_api_token"]
            phone_list = f["phone_list"]
            twillio_url = f["twillio_url"]
            origin_number = f["origin_number"]
            twillio_notification(twillio_api_token, phone_list, twillio_url, origin_number, message)
            sleep(60)
