#!/usr/bin/env python3

import os, pathlib, sys, subprocess, requests, json, argparse, re

def tsschecker(path, device: str, ios: str, build: str, board: str, ecid: str) -> subprocess.CompletedProcess:
    tsschk = subprocess.run([str(path), "--device", device, "--ios", ios, "--buildid", build, "--boardconfig", board, "--no-baseband", "-s", "-e", ecid, "--generator", "0x1111111111111111"], capture_output=True, universal_newlines=False)
    for line in tsschk.stdout.split(b'\n'):
        if b"from" in line:
            print("iOS", ios, build, "wasn't cached so it was downloaded.")
        if b"iOS" == line[:3]:
            print(line.decode())
    return tsschk

def get_json(url):
    return requests.post(url).json()

def get_vers(device: str) -> [str]:
    device_data = get_json(f"https://api.ipsw.me/v4/device/{device}")
    ios_vers = [x['version'] for x in device_data['firmwares']]
    ios_vers.reverse()
    return list(dict.fromkeys(ios_vers))

def run(path, device: str, board: str, ecid: str):
    tsschk = {}
    ios_vers = get_vers(device)
    print('Saving blobs for: device: [', device, '] board: [', board, '] ios:', ios_vers)
    for ios in ios_vers:
        ver_data = get_json(f"https://api.ipsw.me/v4/ipsw/{ios}")
        tsschk[ios] = [tsschecker(path, device, ios, data['buildid'], board, ecid) for data in ver_data if data['identifier'] == device]
    return tsschk

def check_tsschecker():
    ret = True
    if os.path.isfile('/usr/bin/tsschecker') == False:
        ret = False
    else:
        return True
    if os.path.isfile('/usr/local/bin/tsschecker') == False:
        ret = False
    else:
        return True
    return ret

def main():
    tsschecker_path = str("/usr/local/bin/tsschecker")
    if check_tsschecker() == False:
        print("TSSChecker not installed.")
        tsschecker_path = str(input("Please drag in tsschecker executable: ").rstrip())
    parser = argparse.ArgumentParser()
    parser.add_argument('device', help='Your device identifier. EG: iPhone8,1 iPod5,1')
    parser.add_argument('board', help='Your device\'s board config. EG: n71ap n78ap')
    parser.add_argument('ecid', help='Your device\'s ecid in hex. EG: 2143c7dbe8f')
    args = parser.parse_args()
    ret = run(tsschecker_path, args.device, args.board, args.ecid)
    return 0

if __name__ == '__main__':
    sys.exit(main())