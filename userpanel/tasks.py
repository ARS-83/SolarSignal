from django_q.tasks import async_task
from .models import Product
from datetime import datetime
import httpx
import asyncio


import time
import random
import emoji
import logging
import psycopg2
from ProccessSignals import process_signals
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

con = psycopg2.connect(
    database="SolarSignal",
    user="postgres",
    password="123",
    host="localhost",
    port="5432",
)
cur = con.cursor()

async def main():
    while True:
        accounts = None
        with open("accounts.json", "r") as f:
            accounts = json.load(f)
        if accounts == []:
            logger.warning("No accounts found. Sleeping for 120 seconds.")
            time.sleep(120)
            continue

        headers = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0',
  'Accept': 'application/json',
  'Accept-Language': 'en-US,en;q=0.5',
  'Accept-Encoding': 'gzip, deflate, br, zstd',
  'Content-Type': 'application/json',
  'Referer': 'https://club.caronlineofficial.com/login',
  'Access-Control-Allow-Origin': 'application/x-www-form-urlencoded',
  'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept',
  'Origin': 'https://club.caronlineofficial.com',
  'Sec-Fetch-Dest': 'empty',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Site': 'same-origin',
  'Connection': 'keep-alive',
  'Priority': 'u=0',
  'TE': 'trailers'
}
        async with httpx.AsyncClient() as client:
            rand = random.randint(0, len(accounts) - 1)
            response = await client.post(
                "https://club.caronlineofficial.com/api/EmailToken/Login",
                data=json.dumps(accounts[rand]),
                headers=headers,
            )
            response = json.loads(response.text)

            if response["isSuccess"] == True:
                with open("accounts.json", "w") as f:
                    accounts[rand]["token"] = response["data"]
                    f.write(json.dumps(accounts))
                logger.info("Successfully logged in and updated token for account.")
            else:
                logger.error("Login failed for account.")
                continue

            # GET SIGNALS AT API AND PROCESS
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
                "Accept": "application/json",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Referer": "https://club.caronlineofficial.com/chat",
                "Access-Control-Allow-Origin": "application/x-www-form-urlencoded",
                "Access-Control-Allow-Headers": "Origin, X-Requested-With, Content-Type, Accept",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "Authorization": "Bearer {}".format(response["data"]),
                "Connection": "keep-alive",
                "Priority": "u=0",
                "TE": "trailers",
            }
            response = await client.get(
                "https://club.caronlineofficial.com/api/Chat/GetMessages",
                headers=headers,
            )
            data = response.text
            data = emoji.demojize(data)
            data = data.encode("utf-8")
            response = list(json.loads(data))
            if len(response) > 0:
                response.reverse()
                cur.execute("SELECT * FROM userpanel_signal ORDER BY date_added DESC LIMIT 1")
                last_signal = cur.fetchone()
                response = process_signals(response)

                if last_signal is None:
                    i = 0
                    while i < 9:
                        try:
                            signal = response[0]
                            cur.execute(
                                "INSERT INTO userpanel_signal(date_added, signal_text,is_free,currency,leverage,status,margin,signal_type,entry_price,signal_code,stop_loss) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                (
                                    signal["send_time"],
                                    signal["text"],
                                    False,
                                    signal["currency"],
                                    signal["leverage"],
                                    signal["status"],
                                    signal["margin"],
                                    signal["trade_type"],
                                   str(signal["entry"]),
                                    signal["id"],
                                    signal["stop_loss"],
                                ),
                            )
                            con.commit()
                            response.pop(0)
                            i += 1
                            for signal_profit in signal["take_profits"]:
                                cur.execute("INSERT INTO SignalProfit (signal_id, signal_profit,is_outed,is_lossed) VALUES (%s, %s,?,?)", (cur.lastrowid, signal_profit,False,False))
                            logger.info("Signal inserted successfully.")
                        except Exception as e:
                            logger.error(f"Error inserting signal: {e}")
                            con.rollback()
                    con.commit()
                else:
                    arws =23
                    bsit = " AASRD AAAAAAAIS  "
                    signals = cur.execute("SELECT * FROM userpanel_signal ORDER BY date_added DESC LIMIT 10")

                    if signals[0][7]!= response[0]["id"]:
                            
                        for signal in signals:
                            signal = response[0]
                            cur.execute(
                                "INSERT INTO Signal(date_added, signal_text,is_free,currency,leverage,status,margin,signal_type,entry_price,signal_code,stop_loss) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                (
                                    signal["send_time"],
                                    signal["text"],
                                    False,
                                    signal["currency"],
                                    signal["leverage"],
                                    signal["status"],
                                    signal["margin"],
                                    signal["trade_type"],
                                    signal["entry"],
                                    signal["id"],
                                    signal["stop_loss"],
                                ),
                            )
                            con.commit()
                            response.pop(0)
                            i += 1
                            for signal_profit in signal["take_profits"]:
                                cur.execute("INSERT INTO SignalProfit (signal_id, signal_profit,is_outed,is_lossed) VALUES (%s, %s,?,?)", (cur.lastrowid, signal_profit,False,False))
                    while i < 9:

                        cur.execute(
                        "UPDATE userpanel_signal SET status = %s WHERE signal_code = %s",
                        (response[0]["status"], response[0]["id"]),)
                        i+=1
                    con.commit()
                    logger.info("Signal inserted successfully.")

            else:
                logger.warning("No new signals found.")
                continue
