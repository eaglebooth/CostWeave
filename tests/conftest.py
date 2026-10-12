import inspect
import os
import pytest

@pytest.fixture(autouse=True)
def deferred_loader_temp_cleanup(monkeypatch):
    original, pending = os.unlink, []
    def unlink(path, *args, **kwargs):
        try:
            return original(path, *args, **kwargs)
        except PermissionError:
            caller = inspect.currentframe().f_back
            if os.name == "nt" and caller.f_code.co_name == "_inject_message_to_fd0" and caller.f_code.co_filename.replace("\\", "/").endswith("gltest/direct/loader.py"):
                pending.append(path); return None
            raise
    monkeypatch.setattr(os, "unlink", unlink)
    yield
    for path in pending:
        try: original(path)
        except (PermissionError, FileNotFoundError): pass

