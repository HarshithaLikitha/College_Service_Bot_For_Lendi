import importlib.util
import sys

spec = importlib.util.spec_from_file_location("app_mod", "backend/app.py")
app_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_mod)

app = getattr(app_mod, 'app', None)
if app is None:
    print('ERROR: Flask `app` object not found in backend/app.py')
    sys.exit(2)

client = app.test_client()
resp = client.get('/health')
print('STATUS', resp.status_code)
print(resp.get_data(as_text=True))
