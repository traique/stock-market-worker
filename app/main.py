import time
import schedule

from worker import update_prices


def run():
    update_prices()


# chạy mỗi 5 phút
schedule.every(5).minutes.do(run)

print("Market worker started...")

run()

while True:
    schedule.run_pending()
    time.sleep(1)
