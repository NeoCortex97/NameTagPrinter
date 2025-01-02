import json
import pathlib
import urllib.request
import urllib.request
from json import JSONDecodeError
from urllib.error import HTTPError, URLError

import requests
import spacedirectory.directory
import spacedirectory.directory
from urllib3.exceptions import MaxRetryError, NameResolutionError
from rich.progress import track

spaces: list

image_path = pathlib.Path('../../assets/images/raw')

if not image_path.exists():
    image_path.mkdir(parents=True, exist_ok=True)

try:
    spaces = json.load(pathlib.Path('../../data/spaces.json').open('r'))
except FileNotFoundError or JSONDecodeError:
    spaces = []

counter = 0
for name, url in track(spacedirectory.directory.get_spaces_list().items()):
    print(f'{name}: {url}', end='')
    data: dict = {}
    if name in [s['space'] for s in spaces]:
        print(' SKIPPED', end='')
        data = {s['space']: s for s in spaces}[name]
    else:
        try:
            data = {key: value for key, value in json.loads(requests.request('get', url).text).items() if key in ['space', 'url', 'logo']}
            if 'space' not in data.keys():
                print(' WRONG DATA')
                continue
            spaces.append(data)
            counter += 1
            print(' OK', end='')

        except json.JSONDecodeError as e:
            pass
        except requests.ConnectionError as e:
            pass
        except MaxRetryError:
            pass
        except NameResolutionError:
            pass


    if 'logo' not in data.keys():
        print(' NO LOGO DATA')
        continue

    print(' LOGO', data['logo'], '', end='')
    logo_path = pathlib.Path('../../assets/images/raw').joinpath(
        f'{data["space"].replace(" ", "_").replace(".", "").replace("/", "_")}.png')
    if logo_path.exists():
        print('SKIPPED')
        continue
    if 'logo' not in data.keys():
        print('SKIPPED')
        continue

    try:
        urllib.request.urlretrieve(data['logo'], logo_path)
        print('OK')
    except HTTPError:
        print('FAILED')
    except URLError:
        print('FAILED')
    except ValueError:
        print('FAILED')

print(f'Added {counter} spaces')

with pathlib.Path('../../data/spaces.json').open('w') as file:
    json.dump(spaces, file)
