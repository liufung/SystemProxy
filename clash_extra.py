#!python3.9
# -*- encoding: utf-8 -*-

import requests, yaml
from typing import Any, Dict, List

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

clash_output_file: str = './dist/clash_config_extra.yaml'
clash_output_tpl: str = './clash.config.template.yaml'

clash_extra: List[str] = ['https://free886.herokuapp.com/clash/proxies', 'https://free.dswang.ga/clash/proxies',
                          'https://proxy.yugogo.xyz/clash/proxies', 'https://gfwglass.tk/clash/proxies', 'https://free.jingfu.cf/clash/proxies']

blacklist: List[str] = list(
    map(lambda l: l.replace('\r', '').replace('\n', '').split(':'), open('blacklists.txt').readlines()))


def clash_urls() -> List[str]:
    '''
    Fetch URLs For Clash
    '''
    return clash_extra


def fetch_html(url: str) -> str:
    '''
    Fetch The Content Of url
    '''
    try:
        resp: requests.Response = requests.get(url, verify=False, timeout=10)
        if resp.status_code != 200:
            print(f'[!] Got HTTP Status Code {resp.status_code}')
            return None
        return resp.text
    except Exception as e:
        print(f'[-] Error Occurs When Fetching Content Of {url}')
        return None


def merge_clash(configs: List[str]) -> str:
    '''
    Merge Multiple Clash Configurations
    '''
    config_template: Dict[str, Any] = yaml.safe_load(open(clash_output_tpl, encoding='utf-8').read())
    proxies: List[Dict[str, Any]] = []
    for i in range(len(configs)):
        tmp_config: Dict[str, Any] = yaml.safe_load(configs[i])
        if 'proxies' not in tmp_config: continue
        for j in range(len(tmp_config['proxies'])):
            proxy: Dict[str, Any] = tmp_config['proxies'][j]
            if any(filter(lambda p: p[0] == proxy['server'] and str(p[1]) == str(proxy['port']), blacklist)): continue
            if any(filter(lambda p: p['server'] == proxy['server'] and p['port'] == proxy['port'], proxies)): continue
            proxy['name'] = proxy['name'] + f'_{i}@{j}'
            proxies.append(proxy)
    node_names: List[str] = list(map(lambda n: n['name'], proxies))
    config_template['proxies'] = proxies
    for grp in config_template['proxy-groups']:
        if 'xxx' in grp['proxies']:
            grp['proxies'].remove('xxx')
            grp['proxies'].extend(node_names)

    return yaml.safe_dump(config_template, indent=1, allow_unicode=True)


def merge_v2ray(configs: List[str]) -> str:
    '''
    Merge Multiple V2Ray Configurations
    '''
    return '\n'.join(configs)


def main():
    clash_url_list: List[str] = clash_urls()
    # v2ray_url_list:List[str] = v2ray_urls(rss_text)
    print(f'[+] Got {len(clash_url_list)} Clash URLs')

    clash_configs: List[str] = list(
        filter(lambda h: h is not None and len(h) > 0, map(lambda u: fetch_html(u), clash_url_list)))
    # v2ray_configs:List[str] = list(filter(lambda h: h is not None and len(h) > 0, map(lambda u: fetch_html(u), v2ray_url_list)))

    clash_merged: str = merge_clash(clash_configs)
    # v2ray_merged:str = merge_v2ray(v2ray_configs)

    with open(clash_output_file, 'w', encoding='utf-8') as f: f.write(clash_merged)
    # with open(v2ray_output_file, 'w') as f: f.write(v2ray_merged)


if __name__ == '__main__':
    main()
