import base64
import os
import platform
import signal
import sys
import time
import subprocess
from typing import List

import requests
import json

from tqdm import tqdm

parser_version = '1.9.1'
parser_port = 8889

parser_cmd_line = [
    "java",
    "-jar",
    f"document-parser-{parser_version}.jar",
    f"--server.port={parser_port}"
]

headers = {
    'Content-type': 'application/json',
    'Accept': 'application/json; text/plain'
}

parser_url = f"http://localhost:{parser_port}/"
java_subprocess = None

retries = 32


def check_if_parser_is_running() -> bool:
    global java_subprocess
    try:
        requests.get(
            f"{parser_url}status",
            headers=headers
        )
        print('Парсер уже запущен')
        return True
    except Exception:
        print(f'Запуск document-parser на {parser_port} порту, попытки:')

        try:
            java_subprocess = subprocess.Popen(parser_cmd_line,
                                               # creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                                               stdout=subprocess.PIPE,
                                               encoding="utf-8")
            time.sleep(2)
            for i in tqdm(range(retries)):
                # time.sleep(0.1)
                output_log_spring = java_subprocess.stdout.readline()
                # sys.stdout.write("\rПроверка соединения\n")
                sys.stdout.flush()
                if output_log_spring.find("Started DocumentParserService") != -1:
                    print("\nГотово")
                    java_subprocess.stdout.close()
                    break

            if i > 30:
                raise Exception("Не удалось получить доступ к ранее запущенному парсеру")

            print("Сервер парсера запущен успешно")

        except Exception as e:
            print(e)
            return False
        return True


def send_document(data: bytes, doc_type: str) -> List[object]:
    response = requests.post(
        f"{parser_url}document-parser",
        data=json.dumps({
            "base64Content": str(base64.b64encode(data))[2:-1],
            # "base64Content": base64.b64encode(data).decode('ascii'),
            "documentFileType": doc_type
        }),
        headers=headers,
        timeout=15
    )
    if 'message' in response.json():
        raise Exception(response.json()['message'])

    array_of_docs: List[object] = []
    if response.json().get('documents', False):
        array_of_docs = response.json()['documents']

    if not array_of_docs:
        raise Exception('file don`t have docs')

    return array_of_docs


def kill_java_process():
    if java_subprocess is not None:
        if platform.system() == 'Windows':
            subprocess.run("TASKKILL /F /PID {pid} /T".format(pid=java_subprocess.pid))
        elif platform.system() == 'Linux':
            os.kill(java_subprocess.pid, signal.SIGTERM)
        else:
            print('Неизвестная платформа')
