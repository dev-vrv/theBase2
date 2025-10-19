import json
import time
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from .client import send_lead, edit_message, answer_callback_query

@csrf_exempt
def webhook(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST only")

    update = json.loads(request.body.decode("utf-8"))

    cq = update.get("callback_query")
    if not cq:
        return HttpResponse("no callback")

    data = cq.get("data", "")
    if not data.startswith("take:"):
        answer_callback_query(cq.get("id"), "Неизвестное действие")
        return HttpResponse("ok")

    created_ts = int(data.split(":")[1])
    now = int(time.time())
    elapsed = now - created_ts

    mins, secs = divmod(elapsed, 60)
    delta = f"{mins} мин {secs} сек" if mins else f"{secs} сек"

    msg = cq["message"]
    text = msg["text"] + f"\n⏱ <b>Принята:</b> {time.strftime('%H:%M:%S')} (спустя {delta})" \
                         f"\n✅ <b>Взял:</b> @{cq['from'].get('username','user')}"
    edit_message(msg["chat"]["id"], msg["message_id"], text)
    answer_callback_query(cq["id"], "Заявка за тобой ✅")
    return HttpResponse("ok")

@csrf_exempt
def test_send(request):
    """ручной тест через браузер"""
    mid = send_lead("Тест", "+79999999999", ["Матча", "Мохито"], int(time.time()))
    return HttpResponse(f"OK {mid}")
