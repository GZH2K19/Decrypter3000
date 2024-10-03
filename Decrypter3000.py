#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sys import argv
from pathlib import Path
import os
import json

def transEncKey(key:str):
    import hashlib
    md5 = hashlib.md5(key.encode()).hexdigest()
    lis = [int(md5[i:i+2], 16) for i in range(0, len(md5), 2)]
    lis += lis[::-1]
    return lis

def decrypt(data:bytes, tEncKey:list[int]):
    try:
        header = ",".join("{:02x}".format(i) for i in data[:32])
        if header != "41,52,54,00,45,4e,43,52,59,50,54,45,52,31,30,30,46,52,45,45,00,56,45,52,53,49,4f,4e,00,00,00,00":
            raise Exception
        num = min(len(data), len(tEncKey))
        data = bytearray(data[num:])
        for i in range(num):
            data[i] ^= tEncKey[i]
        return bytes(data)
    except:
        return


def process_game(game_path:str):
    game = Path(game_path)
    print("Processing:", game)

    json_system = game/"data"/"System.json"
    if not json_system.exists():
        print("Error: System.json not found.\n")
        return
    with open(json_system, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    encKey = data.get("encryptionKey")
    if not encKey:
        print("Error: Encryption key not found.\n")
        return
    print("Encryption key:", encKey)
    tEncKey = transEncKey(encKey)

    folderList = []
    if data.get("hasEncryptedImages"):
        folderList.append("img")
    if data.get("hasEncryptedAudio"):
        folderList.append("audio")
    if not folderList:
        print("Error: Encrypted files not found.\n")
        return
    
    for folder in folderList:
        print("Decrypting", folder, "files...")
        ori = game/folder
        new = game/(folder+"_decrypted")
        for r in ori.rglob("*.*_"):
            with open(r, "rb") as f:
                byt = decrypt(f.read(), tEncKey)
            if not byt:
                print("Failed to decrypt:", r.relative_to(game))
                continue
            file = str(new/r.relative_to(ori))[:-1]
            os.makedirs(os.path.dirname(file), exist_ok=True)
            with open(file, "wb") as f:
                f.write(byt)
    print("Done.\n")


if __name__ == "__main__":
    if not argv[1:]:
        print("No arguments provided. Please drag the game folder onto this script.")
    else:
        try:
            for game_path in argv[1:]:
                process_game(game_path)
        except:
            from traceback import format_exc
            print(format_exc())
    os.system("pause")
