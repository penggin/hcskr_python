import asyncio
from base64 import b64decode, b64encode
import aiohttp
from .mapping import schoolinfo

import base64
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.PublicKey import RSA

versioninfo = "1.7.0"


def encrypt(n):
    pubkey = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA81dCnCKt0NVH7j5Oh2+SGgEU0aqi5u6sYXemouJWXOlZO3jqDsHYM1qfEjVvCOmeoMNFXYSXdNhflU7mjWP8jWUmkYIQ8o3FGqMzsMTNxr+bAp0cULWu9eYmycjJwWIxxB7vUwvpEUNicgW7v5nCwmF5HS33Hmn7yDzcfjfBs99K5xJEppHG0qc+q3YXxxPpwZNIRFn0Wtxt0Muh1U8avvWyw03uQ/wMBnzhwUC8T4G5NclLEWzOQExbQ4oDlZBv8BM/WxxuOyu0I8bDUDdutJOfREYRZBlazFHvRKNNQQD2qDfjRz484uFs7b5nykjaMB9k/EJAuHjJzGs9MMMWtQIDAQAB=="
    rsa_public_key = b64decode(pubkey)
    pub_key = RSA.importKey(rsa_public_key)

    cipher = Cipher_pkcs1_v1_5.new(pub_key)
    msg = n.encode('utf-8')

    default_encrypt_length = 245
    length = default_encrypt_length
    msg_list = [msg[i:i + length] for i in list(range(0, len(msg), length))]
    encrypt_msg_list = []
    for msg_str in msg_list:
        cipher_text = base64.b64encode(cipher.encrypt(message=msg_str))
        encrypt_msg_list.append(cipher_text)
    return encrypt_msg_list[0].decode("utf-8")


def selfcheck(name, birth, area, schoolname, level, customloginname=None, loop=asyncio.get_event_loop()):
    return loop.run_until_complete(asyncSelfCheck(name, birth, area, schoolname, level, customloginname))


async def asyncSelfCheck(name, birth, area, schoolname, level, customloginname=None):
    if customloginname == None:
        customloginname = name
    else:
        pass
    name = encrypt(name)  # Encrypt Name
    birth = encrypt(birth)  # Encrypt Birth
    try:
        info = schoolinfo(area, level)  # Get schoolInfo from Hcs API
    except:
        return {"error": True, "code": "FORMET", "message": "지역명이나 학교급을 잘못 입력하였습니다."}
    url = f"https://hcs.eduro.go.kr/v2/searchSchool?lctnScCode={info['schoolcode']}&schulCrseScCode={info['schoollevel']}&orgName={schoolname}&loginType=school"

    # REST Client open
    async with aiohttp.ClientSession() as session:
        # Get Request to given Url
        async with session.get(url) as response:
            school_infos = await response.json()

            if len(school_infos["schulList"]) > 5:
                return {
                    "error": True,
                    "code": "NOSCHOOL",
                    "message": "너무 많은 학교가 검색되었습니다. 지역, 학교급을 제대로 입력하고 학교 이름을 보다 상세하게 적어주세요.",
                }

            try:
                schoolcode = school_infos["schulList"][0]["orgCode"]
            except:
                return {
                    "error": True,
                    "code": "NOSCHOOL",
                    "message": "검색 가능한 학교가 없습니다. 지역, 학교급을 제대로 입력하였는지 확인해주세요.",
                }

        # Trying Login Session for get auth token

        data = {"orgCode": schoolcode, "name": name, "birthday": birth, "loginType": "school", "stdntPNo": None}
        requrl = f"https://{info['schoolurl']}hcs.eduro.go.kr/v2/findUser"

        async with session.post(requrl, json=data) as response:
            res = await response.json()
            try:
                token = res["token"]
            except:
                return {
                    "error": True,
                    "code": "NOSTUDENT",
                    "message": "학교는 검색하였으나, 입력한 정보의 학생을 찾을 수 없습니다.",
                }

        # Hcs getUserInfo Request
        endpoint = f"https://{info['schoolurl']}hcs.eduro.go.kr/v2/getUserInfo"
        headers = {"Content-Type": "application/json", "Authorization": token}
        async with session.post(endpoint, json={}, headers=headers) as response:
            try:
                res = await response.json()
                token = res['token']
            except:
                return {"error": True, "code": "UNKNOWN", "message": "getUserInfo: 알 수 없는 에러 발생."}
        # Servey Register
        endpoint = f"https://{info['schoolurl']}hcs.eduro.go.kr/registerServey"
        headers = {"Content-Type": "application/json", "Authorization": token}
        surveydata = {"rspns01": "1", "rspns02": "1", "rspns00": "Y",
                      "upperToken": token, "upperUserNameEncpt": customloginname}

        async with session.post(endpoint, json=surveydata, headers=headers) as response:
            res = await response.json()
            try:
                return {
                    "error": False,
                    "code": "SUCCESS",
                    "message": "성공적으로 자가진단을 수행하였습니다.",
                    "regtime": res["registerDtm"],
                }
            except:
                return {"error": True, "code": "UNKNOWN", "message": "알 수 없는 에러 발생."}
