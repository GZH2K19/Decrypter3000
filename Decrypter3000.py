from sys import argv
from pathlib import Path
import json


class E3000D:
    """3000 Decrypter"""
    HEADER_STR = "41,52,54,00,45,4e,43,52,59,50,54,45,52,31,30,30,46,52,45,45,00,56,45,52,53,49,4f,4e,00,00,00,00"
    def __init__(self, key:str):
        self.key = self.trans_key(key)
        self.key_len = len(self.key)

    @staticmethod
    def trans_key(key:str):
        import hashlib
        md5 = hashlib.md5(key.encode()).hexdigest()
        lis = [int(md5[i:i+2], 16) for i in range(0, len(md5), 2)]
        return lis + lis[::-1]
    
    def decrypt(self, data:bytes):
        try:
            header = ','.join("{:02x}".format(i) for i in data[:32])
            if header != E3000D.HEADER_STR:
                raise Exception("Invalid E3000 header")
            leng = min(len(data), self.key_len)
            data = bytearray(data[leng:])
            for i in range(leng):
                data[i] ^= self.key[i]
            return bytes(data)
        except:
            return None
    
class NKD:
    """No-Key Decrypter"""
    HEADER_STR = "89,50,4E,47,0D,0A,1A,0A,00,00,00,0D,49,48,44,52"
    def __init__(self):
        self.HEADER_LEN = 16
        self.HEADER = self.get_header(self.HEADER_LEN)

    @staticmethod
    def get_header(header_len:int=16):
        header_array = NKD.HEADER_STR.split(',')
        png_header = bytearray(header_len)
        for r in range(header_len):
            png_header[r] = int(header_array[r], 16)
        return png_header

    def decrypt(self, data:bytes):
        data = data[self.HEADER_LEN*2:]
        arr = bytearray(self.HEADER_LEN + len(data))
        arr[:self.HEADER_LEN] = self.HEADER
        arr[self.HEADER_LEN:] = data
        return arr

def process_project(project_path:Path):
    print("Processing:", project_path)

    sys_json = project_path / "data/System.json"
    if not sys_json.exists():
        print("Error: System.json not found.\n")
        return
    with open(sys_json, "r", encoding="utf-8-sig") as f:
        sys_info = json.load(f)
    folderList = []
    if sys_info.get("hasEncryptedImages"):
        folderList.append("img")
    if sys_info.get("hasEncryptedAudio"):
        folderList.append("audio")
    if not folderList:
        print("Warning: Encrypted files not found.\n")
        return
    
    if (project_path / "js/plugins/Art_Decrypterator3000.js").exists():
        dec_type = "E3000"
        encKey = sys_info.get("encryptionKey")
        if not encKey:
            print("Error: Encryption key not found.\n")
            return
        print("Encryption key:", encKey)
        decrypter = E3000D(encKey)
    else:
        dec_type = "default"
        decrypter = NKD()
    print("Decryption type:", dec_type)
    
    for folder in folderList:
        print("Decrypting folder:", folder)
        ori = project_path / folder
        new = project_path / (folder+"_dec")
        for file in ori.rglob("*.*_"):
            with open(file, "rb") as f:
                data = decrypter.decrypt(f.read())
            if not data:
                print("Failed to decrypt:", file.relative_to(project_path))
                continue
            new_file = new / file.relative_to(ori).parent / file.name[:-1]
            new_file.parent.mkdir(parents=True, exist_ok=True)
            with open(new_file, "wb") as f:
                f.write(data)
    print("Done.\n")


if __name__ == "__main__":
    if not argv[1:]:
        print("No arguments provided. Please drag the project folder onto this script.\n")
    else:
        for path in argv[1:]:
            try:
                process_project(Path(path))
            except:
                from traceback import format_exc
                print(format_exc(), '\n')
    input("Press ENTER to exit...")
