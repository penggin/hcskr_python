import asyncio
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_PKCS1_v1_5
from base64 import b64decode, b64encode
import aiohttp

from .mapping import schoolinfo

versioninfo = "1.5.2"


def encrypt(n):
    pubkey = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA81dCnCKt0NVH7j5Oh2+SGgEU0aqi5u6sYXemouJWXOlZO3jqDsHYM1qfEjVvCOmeoMNFXYSXdNhflU7mjWP8jWUmkYIQ8o3FGqMzsMTNxr+bAp0cULWu9eYmycjJwWIxxB7vUwvpEUNicgW7v5nCwmF5HS33Hmn7yDzcfjfBs99K5xJEppHG0qc+q3YXxxPpwZNIRFn0Wtxt0Muh1U8avvWyw03uQ/wMBnzhwUC8T4G5NclLEWzOQExbQ4oDlZBv8BM/WxxuOyu0I8bDUDdutJOfREYRZBlazFHvRKNNQQD2qDfjRz484uFs7b5nykjaMB9k/EJAuHjJzGs9MMMWtQIDAQAB"
    msg = n
    keyDER = b64decode(pubkey)

    keyPub = RSA.importKey(keyDER)
    cipher = Cipher_PKCS1_v1_5.new(keyPub)
    cipher_text = cipher.encrypt(msg.encode())
    emsg = b64encode(cipher_text)
    return emsg.decode("utf-8")


def selfcheck(name, birth, area, schoolname, level, loop=asyncio.get_event_loop()):
    return loop.run_until_complete(asyncSelfCheck(name, birth, area, schoolname, level))


async def asyncSelfCheck(name, birth, area, schoolname, level):
    name = encrypt(name)  # encrypt name
    birth = encrypt(birth)  # encrypt birth
    try:
        info = schoolinfo(area, level)  # get schoolinfo as dictionary data.
    except:
        return {"error": True, "code": "FORMET", "message": "지역명이나 학교급을 잘못 입력하였습니다."}
    url = "https://{}hcs.eduro.go.kr/school?lctnScCode={}&schulCrseScCode={}&orgName={}&currentPageNo=1".format(
        info["schoolurl"], info["schoolcode"], info["schoollevel"], schoolname
    )

    # open aiohttp.ClientSession
    async with aiohttp.ClientSession() as session:
        # get school organization code using given school code
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

        # login with given school data
        data = {"orgcode": schoolcode, "name": name, "birthday": birth}
        requrl = "https://{}hcs.eduro.go.kr/loginwithschool".format(info["schoolurl"])

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

        # post diagnosis information
        endpoint = "https://{}hcs.eduro.go.kr/registerServey".format(info["schoolurl"])
        headers = {"Content-Type": "application/json", "Authorization": token}
        surveydata = {"rspns01":"1","rspns02":"1","rspns03":null,"rspns04":null,"rspns05":null,"rspns06":null,"rspns07":null,"rspns08":null,"rspns09":"0","rspns10":null,"rspns11":null,"rspns12":null,"rspns13":null,"rspns14":null,"rspns15":null,"rspns00":"Y","deviceUuid":"","upperToken":token,"upperUserNameEncpt":name}

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