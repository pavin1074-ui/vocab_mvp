import os
import time
import json
import base64
import tempfile
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FUSIONBRAIN_API_KEY")
SECRET_KEY = os.getenv("FUSIONBRAIN_SECRET_KEY")

API_URL = "https://api-key.fusionbrain.ai/"  # по доке
# MODEL_ID больше не нужен, будем брать pipeline_id
class ImageGenerationError(Exception):
    pass


def _auth_headers():
    if not API_KEY or not SECRET_KEY:
        raise ImageGenerationError("FusionBrain API keys are not configured")
    return {
        "X-Key": f"Key {API_KEY}",
        "X-Secret": f"Secret {SECRET_KEY}",
    }


def _get_pipeline_id() -> str:
    headers = _auth_headers()
    resp = requests.get(API_URL + "key/api/v1/pipelines", headers=headers, timeout=30)
    if resp.status_code != 200:
        raise ImageGenerationError(f"Pipeline list error: {resp.status_code} {resp.text}")
    data = resp.json()
    if not data:
        raise ImageGenerationError("No pipelines in FusionBrain response")
    return data[0]["id"]  # первый Kandinsky, как в доке
    # при желании можно кэшировать это значение в глобальной переменной


def generate_image_for_word(prompt: str, width: int = 512, height: int = 512) -> str:
    """
    Генерирует картинку для слова/фразы и возвращает путь к временно сохранённому файлу.
    Файл нужно удалить после использования.
    """
    headers = _auth_headers()
    print("DEBUG FusionBrain prompt:", prompt)

    pipeline_id = _get_pipeline_id()

    # 1. Запрос на генерацию (как в примере из доки)
    params = {
        "type": "GENERATE",
        "numImages": 1,
        "width": width,
        "height": height,
        "generateParams": {
            "query": prompt
        }
    }

    files = {
        "pipeline_id": (None, pipeline_id),
        "params": (None, json.dumps(params), "application/json"),
    }

    run_resp = requests.post(
        API_URL + "key/api/v1/pipeline/run",
        headers=headers,
        files=files,
        timeout=60,
    )
    if run_resp.status_code != 200:
        raise ImageGenerationError(f"Run error: {run_resp.status_code} {run_resp.text}")

    run_data = run_resp.json()
    uuid = run_data.get("uuid")
    if not uuid:
        raise ImageGenerationError("No uuid in FusionBrain run response")

    # 2. Ожидаем результат
    for attempt in range(30):  # до ~30 секунд
        status_resp = requests.get(
            API_URL + f"key/api/v1/pipeline/status/{uuid}",
            headers=headers,
            timeout=30,
        )
        if status_resp.status_code != 200:
            print("FB STATUS RESP:", status_resp.status_code, status_resp.text)
            raise ImageGenerationError(f"Status error: {status_resp.status_code} {status_resp.text}")

        status_data = status_resp.json()
        status = status_data.get("status")
        print(f"FB STATUS attempt={attempt + 1}, status={status}")

        if status == "DONE":
            result = status_data.get("result") or {}
            files_list = result.get("files") or []
            if not files_list:
                raise ImageGenerationError("No files in DONE response")

            img_b64 = files_list[0]
            img_bytes = base64.b64decode(img_b64)

            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
                tf.write(img_bytes)
                print(f"FB IMAGE saved to {tf.name}")
                return tf.name

        if status in ("FAILED", "ERROR"):
            raise ImageGenerationError(f"Generation failed: {status}")

        time.sleep(2)

    raise ImageGenerationError("Generation timeout")
