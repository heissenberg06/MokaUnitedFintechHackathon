"""Test-only yardımcılar: proje kaynak dosyalarını değiştirmeden test etmek için.

Bu proje sıfır bağımlılık ilkesiyle yazıldığı ve dört farklı klasörde aynı isimde
("server.py") modüller bulunduğu için, her birini `importlib` ile **benzersiz bir
modül adı altında** ayrı ayrı yüklüyoruz. Böylece testler birbirini etkilemez ve
projenin gerçek kaynak dosyalarına hiçbir şekilde dokunulmaz.
"""
import importlib.util
import io
import json
import os
import sys
import threading
import time
import urllib.error
import urllib.request
import uuid

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOKO_UNITED = os.path.join(REPO_ROOT, "Moko_United")


def load_module(unique_name, file_path, extra_syspath=None):
    """Verilen dosyayı `unique_name` altında taze bir modül olarak yükler ve döndürür.

    Her çağrı yeni bir modül nesnesi (yeni global durum: LOCK, _RATE, _CACHE, vb.)
    üretir; böylece test sınıfları arasında durum sızıntısı olmaz.
    """
    if extra_syspath and extra_syspath not in sys.path:
        sys.path.insert(0, extra_syspath)
    spec = importlib.util.spec_from_file_location(unique_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[unique_name] = module
    spec.loader.exec_module(module)
    return module


class LiveServer:
    """Bir sunucu modülünün Handler'ını gerçek bir soket üzerinde (127.0.0.1, rastgele
    boş port) çalıştırır. Veri dosyası daima geçici bir klasöre yönlendirilir; gerçek
    projenin data/*.json dosyalarına asla dokunulmaz."""

    def __init__(self, module, tmp_dir, data_filename):
        self.module = module
        self.tmp_dir = tmp_dir
        module.DATA_DIR = tmp_dir
        module.DATA_FILE = os.path.join(tmp_dir, data_filename)
        if hasattr(module, "UPLOAD_DIR"):
            module.UPLOAD_DIR = os.path.join(tmp_dir, "uploads")
        if hasattr(module, "_CACHE"):
            module._CACHE = None
        self.server = module.ThreadingHTTPServer(("127.0.0.1", 0), module.Handler)
        self.port = self.server.server_address[1]
        self.base_url = f"http://127.0.0.1:{self.port}"
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def start(self):
        self.thread.start()
        return self

    def stop(self):
        self.server.shutdown()
        self.server.server_close()

    def __enter__(self):
        return self.start()

    def __exit__(self, *exc):
        self.stop()


def http_json(method, url, payload=None, timeout=5):
    """JSON body ile istek atar; (status, parsed_json) döner. HTTPError'ları da yakalar."""
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                  headers={"Content-Type": "application/json"} if data else {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, (json.loads(body) if body else None)
    except urllib.error.HTTPError as e:
        with e:
            body = e.read().decode("utf-8")
            return e.code, (json.loads(body) if body else None)


def build_multipart(fields, files=None):
    """(content_type, body_bytes) üretir. `files`: [(field_name, filename, content_type, data)]"""
    boundary = uuid.uuid4().hex
    files = files or []
    parts = []
    for name, value in fields.items():
        parts.append(
            f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode("utf-8")
        )
    for name, filename, ctype, data in files:
        header = (
            f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'
            f'Content-Type: {ctype}\r\n\r\n'
        ).encode("utf-8")
        parts.append(header + data + b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode("utf-8"))
    body = b"".join(parts)
    return f"multipart/form-data; boundary={boundary}", body


def http_multipart_post(url, fields, files=None, timeout=5):
    content_type, body = build_multipart(fields, files)
    req = urllib.request.Request(url, data=body, method="POST",
                                  headers={"Content-Type": content_type,
                                           "Content-Length": str(len(body))})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        with e:
            return e.code, json.loads(e.read().decode("utf-8"))
