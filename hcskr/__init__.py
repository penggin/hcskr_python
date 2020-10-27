from .hcs import selfcheck, asyncSelfCheck, encrypt, versioninfo
import requests
import os
import sys
VERSIONINFO = requests.get("https://raw.githubusercontent.com/331leo/hcskr_python/main/VERSIONINFO").text
VERSIONINFO=VERSIONINFO.split("#")
if VERSIONINFO[1] == "M" and VERSIONINFO[0] > versioninfo:
    os.system(f"{sys.executable} -m pip install --upgrade hcskr")
    print("필수 모듈 업데이트가 있습니다. 자동으로 업데이트 하였습니다. 정상적인 작동을 위해 프로그램을 재실행 해주세요")