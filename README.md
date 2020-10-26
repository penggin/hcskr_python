# HCSKR
[![Send mail](https://img.shields.io/badge/-support@leok.kr-63d863?style=flat-square&logo=gmail&logoColor=white&link=mailto:support@leok.kr)](mailto:support@leok.kr) ![Badge](https://img.shields.io/badge/-v0.5.1-9ACD32?style=flat-square&logo=pypi&logoColor=white&link=mailto:support@leok.kr) ![Badge](https://img.shields.io/badge/-v3.x-3776AB?style=flat-square&logo=python&logoColor=white&link=mailto:support@leok.kr)</br>

파이썬용 학생 코로나 자가진단 라이브러리 입니다.
  - https://pypi.org/project/hcskr/
  - https://github.com/331leo/hcskr_python


## 다운로드
**이 모듈은 파이썬 3.6.x ~ 3.8.x 까지의 동작을 보장합니다.
그 이외의 버전에서는 제대로 작동하지 않을 수 있습니다.**

윈도우나 리눅스의 터미널에서 다음과 같이 입력합니다.
```shell
pip install hcskr
```
오류가 나는 경우, ```python -m pip install --upgrade pip``` 로 pip를 업데이트 해주세요.

## 사용법
```python
import hcskr
hcskr.selfcheck("홍길동","030510","서울","두둥실고","고등학교")
#hcskr.selfcheck("이름","생년월일","지역","학교이름","학교종류")
```

## 리턴값

모든 리턴값은 Dict 로 반환됩니다.</br>
리턴값 구조는 다음과 같습니다: </br>```{"error":Boolen(True,False),'code':"처리코드(밑의 처리코드 종류 참조)","message":"해당 에러나, 성공 상황에 대한 설명"}```
  - 반환 될 수 있는 모든 리턴값
  ```
  {"error": False, "code": "SUCCESS", "message": "성공적으로 자가진단을 수행하였습니다."}
  {"error": True, "code": "FORMET", "message": "지역명이나 학교급을 잘못 입력하였습니다."}
  {"error": True, "code": "NOSCHOOL", "message": "너무 많은 학교가 검색되었습니다. 지역, 학교급을 제대로 입력하고 학교 이름을 보다 상세하게 적어주세요."}
  {"error":True,"code":"NOSCHOOL","message":"검색 가능한 학교가 없습니다. 지역, 학교급을 제대로 입력하였는지 확인해주세요."}
  {"error":True,"code":"NOSTUDENT","message":"학교는 검색하였으나, 입력한 정보의 학생을 찾을 수 없습니다."}
  {"error": True, "code": "UNKNOWN", "message": "알 수 없는 에러 발생."}
  ```

<details><summary>처리코드 종류</summary>
성공 = "SUCCESS"</br>  
존재하지 않는 지역, 학교급 = "FORMET"</br>  
학교 검색 실패 = "NOSCHOOL"</br>  
학생 검색 실패 = "NOSTUDENT"</br>  
알 수 없는 에러 = "UNKNOWN" 
</details>

## 예제 코드
```py
import hcskr

name = input("이름을 입력하세요: ")
birth = input("생년월일을 입력하세요: ")
level = input("학교종류를 입력하세요(예: 초등학교, 중학교, 고등학교): ")
region = input("지역을 입력하세요(예: 서울, 경기, 전남....): ")
school = input("학교이름을 입력하세요(예: 두둥실고): ")
```
data = hcskr.selfcheck(name,birth,region,school,level)
print(data['message'])

## 💡 TIP
리턴값의 `'code'` 를 이용하시면 성공, 실패여부, 실패이유를 모두 알 수 있어요!</br>
또한 `'message'`로 이용자에게 바로 실패이유를 알릴수도 있어요!

