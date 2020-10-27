from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_PKCS1_v1_5
from base64 import b64decode, b64encode
import requests
import os
import sys
import json

from .mapping import schoolinfo
versioninfo = "1.5.0"
def encrypt(n):
    pubkey = 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA81dCnCKt0NVH7j5Oh2+SGgEU0aqi5u6sYXemouJWXOlZO3jqDsHYM1qfEjVvCOmeoMNFXYSXdNhflU7mjWP8jWUmkYIQ8o3FGqMzsMTNxr+bAp0cULWu9eYmycjJwWIxxB7vUwvpEUNicgW7v5nCwmF5HS33Hmn7yDzcfjfBs99K5xJEppHG0qc+q3YXxxPpwZNIRFn0Wtxt0Muh1U8avvWyw03uQ/wMBnzhwUC8T4G5NclLEWzOQExbQ4oDlZBv8BM/WxxuOyu0I8bDUDdutJOfREYRZBlazFHvRKNNQQD2qDfjRz484uFs7b5nykjaMB9k/EJAuHjJzGs9MMMWtQIDAQAB'
    msg = n
    keyDER = b64decode(pubkey)
    keyPub = RSA.importKey(keyDER)
    cipher = Cipher_PKCS1_v1_5.new(keyPub)
    cipher_text = cipher.encrypt(msg.encode())
    emsg = b64encode(cipher_text)
    return emsg.decode('utf-8')


def selfcheck(name, birth, area, schoolname, level):
    name = encrypt(name)
    birth = encrypt(birth)
    try:
        info = schoolinfo(area, level)
    except:
        return {"error": True, "code": "FORMET", "message": "지역명이나 학교급을 잘못 입력하였습니다."}
    url = 'https://' + info["schoolurl"] + 'hcs.eduro.go.kr/school?lctnScCode=' + str(
        info["schoolcode"]) + '&schulCrseScCode=' + str(
        info["schoollevel"]) + '&orgName=' + schoolname + '&currentPageNo=1'
    response = requests.get(url)
    school_infos = json.loads(response.text)
    if len(school_infos["schulList"])>5:
        return {"error": True, "code": "NOSCHOOL", "message": "너무 많은 학교가 검색되었습니다. 지역, 학교급을 제대로 입력하고 학교 이름을 보다 상세하게 적어주세요."}
    try:
        schoolcode = school_infos["schulList"][0]["orgCode"]
    except:
        return {"error":True,"code":"NOSCHOOL","message":"검색 가능한 학교가 없습니다. 지역, 학교급을 제대로 입력하였는지 확인해주세요."}
    data = {"orgcode": schoolcode, "name": name, "birthday": birth}
    requrl="https://"+info["schoolurl"]+"hcs.eduro.go.kr/loginwithschool"
    response = requests.post(url=requrl, data=json.dumps(data), headers={'Content-Type': 'application/json'})

    try:
        token = response.json()['token']
    except:
        return {"error":True,"code":"NOSTUDENT","message":"학교는 검색하였으나, 입력한 정보의 학생을 찾을 수 없습니다."}
    endpoint = "https://" + info["schoolurl"] + "hcs.eduro.go.kr/registerServey"
    headers = {'Content-Type': 'application/json', "Authorization": token}
    surveydata = {"rspns01": "1", "rspns02": "1", "rspns03": None, "rspns04": None, "rspns05": None, "rspns06": None,
                  "rspns07": "0", "rspns08": "0", "rspns09": "0", "rspns10": None, "rspns11": None, "rspns12": None,
                  "rspns13": None, "rspns14": None, "rspns15": None, "rspns00": "Y", "deviceUuid": ""}
    response = requests.post(endpoint, data=json.dumps(surveydata), headers=headers).json()
    try:
        response['registerDtm']
        return {"error": False, "code": "SUCCESS", "message": "성공적으로 자가진단을 수행하였습니다.",
                "regtime": response['registerDtm']}
    except:
        return {"error": True, "code": "UNKNOWN", "message": "알 수 없는 에러 발생."}


async def asyncSelfCheck(name, birth, area, schoolname, level):
    try:
        import aiohttp
    except:
        os.system(f"{sys.executable} -m pip install aiohttp==3.6.3")

    import aiohttp
    name = encrypt(name)    # encrypt name
    birth = encrypt(birth)  # encrypt birth
    try:
        info = schoolinfo(area, level)  # get schoolinfo as dictionary data.
    except:
        return {"error": True, "code": "FORMET", "message": "지역명이나 학교급을 잘못 입력하였습니다."}
    url = 'https://{}hcs.eduro.go.kr/school?lctnScCode={}&schulCrseScCode={}&orgName={}&currentPageNo=1'\
        .format(info["schoolurl"], info["schoolcode"], info["schoollevel"], schoolname)

    # open aiohttp.ClientSession
    async with aiohttp.ClientSession() as session:
        # get school organization code using given school code
        async with session.get(url) as response:
            school_infos = await response.json()

            if len(school_infos["schulList"]) > 5:
                return {"error": True, "code": "NOSCHOOL", "message": "너무 많은 학교가 검색되었습니다. 지역, 학교급을 제대로 입력하고 학교 이름을 보다 상세하게 적어주세요."}

            try:
                schoolcode = school_infos["schulList"][0]["orgCode"]
            except:
                return {"error": True, "code": "NOSCHOOL", "message": "검색 가능한 학교가 없습니다. 지역, 학교급을 제대로 입력하였는지 확인해주세요."}

        # login with given school data
        data = {"orgcode": schoolcode, "name": name, "birthday": birth}
        requrl='https://{}hcs.eduro.go.kr/loginwithschool'.format(info["schoolurl"])

        async with session.post(requrl, json=data) as response:
            res = await response.json()

            try:
                token = res['token']
            except:
                return {"error": True, "code": "NOSTUDENT", "message": "학교는 검색하였으나, 입력한 정보의 학생을 찾을 수 없습니다."}

        # post diagnosis information
        endpoint = "https://{}hcs.eduro.go.kr/registerServey".format(info["schoolurl"])
        headers = {'Content-Type': 'application/json', "Authorization": token}
        surveydata = {"rspns01": "1", "rspns02": "1", "rspns03": None, "rspns04": None, "rspns05": None, "rspns06": None,
                      "rspns07": "0", "rspns08": "0", "rspns09": "0", "rspns10": None, "rspns11": None, "rspns12": None,
                      "rspns13": None, "rspns14": None, "rspns15": None, "rspns00": "Y", "deviceUuid": ""}

        async with session.post(endpoint, json=surveydata, headers=headers) as response:
            res = await response.json()
            try:
                return {"error": False, "code": "SUCCESS", "message": "성공적으로 자가진단을 수행하였습니다.",
                        "regtime": res['registerDtm']}
            except:
                return {"error": True, "code": "UNKNOWN", "message": "알 수 없는 에러 발생."}


