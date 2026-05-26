import time
import schedule

from worker import update_prices

def run():
    update_prices()

schedule.every(30).seconds.do(run)

print("Market worker started...")

run()

while True:
    schedule.run_pending()
    time.sleep(1)
