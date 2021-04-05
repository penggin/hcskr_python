import asyncio
import sys

import jwt

from base64 import b64decode, b64encode

from .mapping import schoolinfo, encrypt, pubkey
from .request import send_hcsreq, search_school


def selfcheck(
    name: str,
    birth: str,
    area: str,
    schoolname: str,
    level: str,
    password: str,
    customloginname: str = None,
    loop=asyncio.get_event_loop()
):
    return loop.run_until_complete(asyncSelfCheck(name,birth,area,schoolname,level,password,customloginname))


def userlogin(
    name: str, birth: str, area: str, schoolname: str, level: str, password: str, loop=asyncio.get_event_loop()
):
    return loop.run_until_complete(asyncUserLogin(name,birth,area,schoolname,level,password))


def generatetoken(
    name: str, birth: str, area: str, schoolname: str, level: str, password: str, loop=asyncio.get_event_loop()
):
    return loop.run_until_complete(asyncGenerateToken(name,birth,area,schoolname,level,password))


def tokenselfcheck(token: str, loop=asyncio.get_event_loop()):
    return loop.run_until_complete(asyncTokenSelfCheck(token))


async def asyncSelfCheck(
    name: str,
    birth: str,
    area: str,
    schoolname: str,
    level: str,
    password: str,
    customloginname: str = None,
):
    if customloginname is None:
        customloginname = name

    login_result = await asyncUserLogin(name, birth, area, schoolname, level, password)

    if login_result["error"]:
        return login_result

    try:
        res = await send_hcsreq(
            headers={
                "Content-Type": "application/json",
                "Authorization": login_result["token"],
            },
            endpoint="/v2/getUserInfo",
            school=login_result["info"]["schoolurl"],
            json={"orgCode": login_result["schoolcode"]},
        )

        token = res["token"]

    except Exception:
        return {
            "error": True,
            "code": "UNKNOWN",
            "message": "getUserInfo: 알 수 없는 에러 발생.",
        }

    try:
        res = await send_hcsreq(
            headers={
                "Content-Type": "application/json",
                "Authorization": token,
            },
            endpoint="/registerServey",
            school=login_result["info"]["schoolurl"],
            json={
                "rspns01": "1",
                "rspns02": "1",
                "rspns00": "Y",
                "upperToken": token,
                "upperUserNameEncpt": customloginname,
            },
        )

        return {
            "error": False,
            "code": "SUCCESS",
            "message": "성공적으로 자가진단을 수행하였습니다.",
            "regtime": res["registerDtm"],
        }

    except Exception:
        return {"error": True, "code": "UNKNOWN", "message": "알 수 없는 에러 발생."}


async def asyncUserLogin(
    name: str, birth: str, area: str, schoolname: str, level: str, password: str
):
    name = encrypt(name)  # Encrypt Name
    birth = encrypt(birth)  # Encrypt Birth
    password = encrypt(password)  # Encrypt Password

    try:
        info = schoolinfo(area, level)  # Get schoolInfo from Hcs API

    except Exception:
        return {"error": True, "code": "FORMET", "message": "지역명이나 학교급을 잘못 입력하였습니다."}

    school_infos = await search_school(
        code=info["schoolcode"], level=info["schoollevel"], org=schoolname
    )

    if len(school_infos["schulList"]) > 5:
        return {
            "error": True,
            "code": "NOSCHOOL",
            "message": "너무 많은 학교가 검색되었습니다. 지역, 학교급을 제대로 입력하고 학교 이름을 보다 상세하게 적어주세요.",
        }

    try:
        schoolcode = school_infos["schulList"][0]["orgCode"]

    except Exception:
        return {
            "error": True,
            "code": "NOSCHOOL",
            "message": "검색 가능한 학교가 없습니다. 지역, 학교급을 제대로 입력하였는지 확인해주세요.",
        }

    try:
        res = await send_hcsreq(
            headers={"Content-Type": "application/json"},
            endpoint="/v2/findUser",
            school=info["schoolurl"],
            json={
                "orgCode": schoolcode,
                "name": name,
                "birthday": birth,
                "loginType": "school",
                "stdntPNo": None,
            },
        )

        token = res["token"]

    except Exception:
        return {
            "error": True,
            "code": "NOSTUDENT",
            "message": "학교는 검색하였으나, 입력한 정보의 학생을 찾을 수 없습니다.",
        }

    try:
        res = await send_hcsreq(
            headers={"Content-Type": "application/json", "Authorization": token},
            endpoint="/v2/validatePassword",
            school=info["schoolurl"],
            json={"password": password, "deviceUuid": ""},
        )
        if isinstance(res, dict):
            if res["isError"]:
                return {
                    "error": True,
                    "code": "PASSWORD",
                    "message": "학생정보는 검색하였으나, 비밀번호가 틀립니다.",
                }
        
        token = res

    except Exception:
        return {
            "error": True,
            "code": "UNKNOWN",
            "message": "validatePassword: 알 수 없는 에러 발생.",
        }

    try:
        caller_name = str(sys._getframe(1).f_code.co_name)

    except Exception:
        caller_name = None

    if caller_name == "asyncSelfCheck":
        return {
            "error": False,
            "code": "SUCCESS",
            "message": "유저 로그인 성공!",
            "token": token,
            "info": info,
            "schoolcode": schoolcode,
        }

    return {"error": False, "code": "SUCCESS", "message": "유저 로그인 성공!"}


async def asyncGenerateToken(
    name: str, birth: str, area: str, schoolname: str, level: str, password: str
):
    login_result = await asyncUserLogin(**locals())

    if login_result["error"]:
        return login_result

    data = {
        "name": str(name),
        "birth": str(birth),
        "area": str(area),
        "schoolname": str(schoolname),
        "level": str(level),
        "password": str(password),
    }

    jwt_token = jwt.encode(data, pubkey, algorithm="HS256")

    if isinstance(jwt_token, str):
        jwt_token = jwt_token.encode("utf8")

    token = b64encode(jwt_token).decode("utf8")

    return {
        "error": False,
        "code": "SUCCESS",
        "message": "자가진단 토큰 발급 성공!",
        "token": token,
    }


async def asyncTokenSelfCheck(token: str, customloginname: str = None):
    try:
        data = jwt.decode(b64decode(token), pubkey, algorithms="HS256")

    except Exception:
        return {"error": True, "code": "WRONGTOKEN", "message": "올바르지 않은 토큰입니다."}

    return await asyncSelfCheck(
        data["name"],
        data["birth"],
        data["area"],
        data["schoolname"],
        data["level"],
        data["password"],
        customloginname,
    )
