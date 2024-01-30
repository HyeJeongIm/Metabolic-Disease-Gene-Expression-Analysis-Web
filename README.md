# Metabolic-Disease-Gene-Expression-Analysis-Web
유전자 데이터 시각화 사이트

## 🖥 프로젝트 소개
[DevOmics](http://www.devomics.cn/#/)를 참고하여 만든 사이트

## ⏲ 개발 기간
- 2023.12.15 ~

## ⚙ 개발 환경
- Python: 
- Streamlit:
- Pyvis:
- Plotly:
- Pandas:
- Seaborn

## 💿 실행 방법
### 1. Git clone
- 기능 구현마다 실시간으로 code를 업데이트 하여 공유
```shell
git clone https://github.com/HyeJeongIm/Metabolic-Disease-Gene-Expression-Analysis-Web.git
```

### 2. Data 파일 경로
- `main.py`에서 사용될 모든 data는 `data 폴더` 안에 들어간다.
  
  ![image](https://github.com/HyeJeongIm/Metabolic-Disease-Gene-Expression-Analysis-Web/assets/88639757/a548b04c-8edf-442d-a6c9-b917e811222d)

- `Gene Expression 폴더`만 별도로 Raw, Z_Score로 나뉜다.

  ![image](https://github.com/HyeJeongIm/Metabolic-Disease-Gene-Expression-Analysis-Web/assets/88639757/b6bce28c-36d4-4ddb-b92b-aef9ad011e5a)

### 3. Code 실행 방법
#### 3.1. 라이브러리들을 설치하기 위한 python pip 명령어
```shell
pip install -r requirements.txt
```
#### 3.2. 실행 코드
```shell
streamlit run main.py
```
- 코드 실행 전 디렉토리 위치를 확인해줘야 함

  ![image](https://github.com/HyeJeongIm/Metabolic-Disease-Gene-Expression-Analysis-Web/assets/88639757/9197faac-774d-43d7-ac0f-6a34b55fc401)
