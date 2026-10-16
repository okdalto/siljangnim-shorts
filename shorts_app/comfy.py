"""Comfy Router: persistent idempotency, resumable jobs, credential-free evidence."""
import hashlib
import json
import os
import re
import time
import uuid
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = 'https://api.comfy.org'
GEORGE = 'JBFqnCBsd6RMkjVDRZzb'


def save(path, value):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2))
    temporary.replace(path)


def token():
    # File first: a stale shell variable must not shadow a newly saved key.
    path = Path(os.environ.get('COMFY_KEY_FILE', str(Path.home()/'.config/siljangnim-shorts/comfy-token')))
    value = path.read_text().strip() if path.is_file() else os.environ.get('COMFY_API_KEY', '').strip()
    if not value:
        raise RuntimeError('Comfy API key missing; save comfy-token or set COMFY_KEY_FILE')
    return value


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def call(method, path, payload=None, idem=None):
    headers = {'X-API-Key': token(), 'Content-Type': 'application/json'}
    if idem:
        headers['Idempotency-Key'] = idem
    request = urllib.request.Request(BASE + path, method=method, headers=headers,
        data=json.dumps(payload).encode() if payload is not None else None)
    try:
        with urllib.request.build_opener(NoRedirect()).open(request, timeout=60) as response:
            return response.status, response.headers, response.read()
    except urllib.error.HTTPError as e:
        # Do not include response bodies, which may echo credentials or prompts.
        raise RuntimeError(f'Comfy HTTP {e.code}; retry resumes the same request, no provider fallback') from None
    except urllib.error.URLError:
        raise RuntimeError('Comfy unreachable; rerun to resume the same request') from None


def parameters(text, config):
    if config.get('speed', 1) != 1:
        raise ValueError('Use post-production tempo; Comfy dialogue does not accept speed')
    if config.get('voice_id', GEORGE) != GEORGE:
        raise ValueError('Production voice must remain George')
    return {'inputs': [{'text': text, 'voice_id': GEORGE}], 'language_code': 'en',
            'seed': config['seed'], 'settings': {'stability': config['stability']}}


def generate_request(model, payload, folder, timeout=1200):
    if not re.fullmatch(r'[a-z0-9_-]+/[A-Za-z0-9_.-]+', model):
        raise ValueError('Expected provider/model ID')
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    request_file = folder/'request.json'
    record = json.loads(request_file.read_text()) if request_file.exists() else {
        'provider': 'comfy', 'base': BASE, 'model': model, 'params': payload, 'idem_key': uuid.uuid4().hex}
    if any(record.get(k) != v for k, v in {'base': BASE, 'model': model, 'params': payload}.items()):
        raise ValueError('Cached Comfy request differs from requested generation')
    save(request_file, record)
    output = folder/'response.bin'
    evidence = folder/'provider.json'
    if output.is_file() and evidence.is_file():
        meta = json.loads(evidence.read_text())
        if meta.get('sha256') == hashlib.sha256(output.read_bytes()).hexdigest():
            return output
    # Binary ElevenLabs results are currently supported on the synchronous route only.
    if model.startswith('elevenlabs/'):
        _, headers, body = call('POST', '/v2/models/' + model, payload, record['idem_key'])
        pending = folder/'response.pending'
        pending.write_bytes(body)
        pending.replace(output)
        save(evidence, {'provider': 'comfy', 'model': model,
            'request_id': headers.get('X-Request-Id'), 'idem_key': record['idem_key'],
            'content_type': headers.get('Content-Type', ''),
            'sha256': hashlib.sha256(body).hexdigest()})
        return output
    route = '/v2/models/' + model + '/requests'
    if not record.get('request_id'):
        _, _, body = call('POST', route, payload, record['idem_key'])
        record['request_id'] = json.loads(body)['request_id']
        save(request_file, record)
    route += '/' + urllib.parse.quote(record['request_id'], safe='')
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        _, headers, body = call('GET', route + '/status')
        status = json.loads(body)
        if status['status'] == 'COMPLETED':
            if status.get('error_type'):
                raise RuntimeError('Comfy generation failed; existing request retained for inspection')
            code, headers, body = call('GET', route)
            if code != 202:
                pending = folder/'response.pending'
                pending.write_bytes(body)
                pending.replace(output)
                save(evidence, {'provider': 'comfy', 'model': model,
                    'request_id': record['request_id'], 'content_type': headers.get('Content-Type', ''),
                    'sha256': hashlib.sha256(body).hexdigest()})
                return output
        elif status['status'] not in ('IN_QUEUE', 'IN_PROGRESS'):
            raise RuntimeError('Unknown Comfy request status; request retained')
        try:
            delay = float(headers.get('Retry-After', 2))
        except ValueError:
            delay = 2
        time.sleep(max(.1, min(10, delay)))
    raise TimeoutError('Comfy timed out; rerun to resume the existing request')


def generate(text, config, folder):
    model = config['model']
    if model != 'elevenlabs/eleven_v3':
        raise ValueError('Use the approved ElevenLabs v3 model')
    output = generate_request(model, parameters(text, config), folder)
    meta = json.loads((folder/'provider.json').read_text())
    if not meta['content_type'].split(';')[0].startswith(('audio/', 'application/octet-stream')):
        raise RuntimeError('Expected binary Comfy voice audio')
    meta.update(voice=config['voice'], voice_id=GEORGE)
    save(folder/'provider.json', meta)
    return output
