import threading
import time
import schedule

from fastapi import FastAPI
import uvicorn

from worker import update_prices

app = FastAPI()


@app.get("/")
def health():
    return {
        "status": "ok",
        "service": "market-worker",
    }


def run_worker():
    def job():
        update_prices()

    # chạy ngay lần đầu
    job()

    # mỗi 5 phút
    schedule.every(5).minutes.do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)


# chạy worker background thread
threading.Thread(
    target=run_worker,
    daemon=True,
).start()


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=10000,
    )
