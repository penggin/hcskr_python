# HCSKR📱
[![Send mail](https://img.shields.io/badge/-support@leok.kr-63d863?style=flat-square&logo=gmail&logoColor=white&link=mailto:support@leok.kr)](mailto:support@leok.kr) ![Badge](https://img.shields.io/badge/-v1.3.5-9ACD32?style=flat-square&logo=pypi&logoColor=white&link=mailto:support@leok.kr) ![Badge](https://img.shields.io/badge/-v3.x-3776AB?style=flat-square&logo=python&logoColor=white&link=mailto:support@leok.kr)</br>

파이썬용 학생 코로나 자가진단 라이브러리 입니다.
  - https://pypi.org/project/hcskr/
  - https://github.com/331leo/hcskr_python


## 📥다운로드
**이 모듈은 파이썬 3.6.x ~ 3.8.x 까지의 동작을 보장합니다.
그 이외의 버전에서는 제대로 작동하지 않을 수 있습니다.**

윈도우나 리눅스의 터미널에서 다음과 같이 입력합니다.
```shell
pip install hcskr
```
오류가 나는 경우, ```python -m pip install --upgrade pip``` 로 pip를 업데이트 해주세요.

## 🤖사용법
```python
import hcskr
hcskr.selfcheck("홍길동","030510","서울","두둥실고","고등학교")

#hcskr.selfcheck("이름","생년월일","지역","학교이름","학교종류")

#kwargs도 지원합니다 hcskr.selfcheck(birth="생년월일",schoolname="학교이름",area="서울",name="홍길동",level="중학교")
```

<details><summary>▶️지원하는 모든 지역이름 보기</summary>
<p>
지원하는 지역 이름은 다음과 같습니다: 

'서울', '서울시', '서울교육청', '서울시교육청', '서울특별시'</br>
'부산', '부산광역시', '부산시', '부산교육청', '부산광역시교육청'</br> 
'대구', '대구광역시', '대구시', '대구교육청', '대구광역시교육청'</br> 
'인천', '인천광역시', '인천시', '인천교육청', '인천광역시교육청'</br> 
'광주', '광주광역시', '광주시', '광주교육청', '광주광역시교육청'</br> 
'대전', '대전광역시', '대전시', '대전교육청', '대전광역시교육청'</br> 
'울산', '울산광역시', '울산시', '울산교육청', '울산광역시교육청'</br> 
'세종', '세종특별시', '세종시', '세종교육청', '세종특별자치시', '세종특별자치시교육청'</br> 
'경기', '경기도', '경기교육청', '경기도교육청'</br> 
'강원', '강원도', '강원교육청', '강원도교육청'</br> 
'충북', '충청북도', '충북교육청', '충청북도교육청'</br> 
'충남', '충청남도', '충남교육청', '충청남도교육청'</br> 
'전북', '전라북도', '전북교육청', '전라북도교육청'</br> 
'전남', '전라남도', '전남교육청', '전라남도교육청'</br> 
'경북', '경상북도', '경북교육청', '경상북도교육청'</br> 
'경남', '경상남도', '경남교육청', '경상남도교육청'</br> 
'제주', '제주도', '제주특별자치시', '제주교육청', '제주도교육청', '제주특별자치시교육청', '제주특별자치도'
</p>
</details>

<details><summary>▶️지원하는 모든 학교종류 보기</summary>
<p>
지원하는 학교급 이름은 다음과 같습니다: 

'유치원', '유','유치'</br>
'초등학교', '초','초등'</br> 
'중학교', '중','중등'</br> 
'고등학교', '고','고등'</br>
'특수학교', '특','특수','특별'
</p>
</details>

## ↩️리턴값

모든 리턴값은 Dict 로 반환됩니다.</br>
리턴값 구조는 다음과 같습니다: </br>
```
{"error":Boolen(True,False),'code':"처리코드(밑의 처리코드 종류 참조)","message":"해당 에러나, 성공 상황에 대한 설명"}
```

<details><summary>▶️처리코드 종류</summary>
성공 = "SUCCESS"</br>  
존재하지 않는 지역, 학교급 = "FORMET"</br>  
학교 검색 실패 = "NOSCHOOL"</br>  
학생 검색 실패 = "NOSTUDENT"</br>  
알 수 없는 에러 = "UNKNOWN" 
</details>


## 👨‍🏫예제 코드
```py
import hcskr

name = input("이름을 입력하세요: ")
birth = input("생년월일을 입력하세요: ")
level = input("학교종류를 입력하세요(예: 초등학교, 중학교, 고등학교): ")
region = input("지역을 입력하세요(예: 서울, 경기, 전남....): ")
school = input("학교이름을 입력하세요(예: 두둥실고): ")
data = hcskr.selfcheck(name,birth,region,school,level)
print(data['message'])
```
----
```shell
이름을 입력하세요: 홍길동
생년월일을 입력하세요: 030303
학교종류를 입력하세요(예: 초등학교, 중학교, 고등학교): 고등학교
지역을 입력하세요(예: 서울, 경기, 전남....): 서울
학교이름을 입력하세요(예: 두둥실고): 두둥둥실고
검색 가능한 학교가 없습니다. 지역, 학교급을 제대로 입력하였는지 확인해주세요.
```
## 💡 TIP
리턴값의 `'code'` 를 이용하시면 성공, 실패여부, 실패이유를 모두 알 수 있어요!</br>
또한 `'message'`로 이용자에게 바로 실패이유를 알릴수도 있어요!

