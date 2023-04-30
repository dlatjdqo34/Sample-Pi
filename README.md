# Sample-Pi

## 라즈베리 파이로 간단한 샘플러 만들기

### 🎵 샘플러란?

오디오 파일을 피치 변환이나 역재생 등등이 가능하도록 하여 오디오 시퀀싱을 할 때 편한 기능을 제공하는 프로그램

- 이번에는 라즈베리 파이에서 python으로 샘플러를 구현해보도록 했습니다.

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/50c765ad-e6c7-4939-a220-c6c3e2c801e0/Untitled.png)

시간이 많지 않아서 제가 지원하려는 기능은 다음과 같습니다.

1. 초간단 GUI 제공 `tkinter`
2. wav 파일을 업로드 하여 샘플링이 가능하도록 구현
3. 지원하는 샘플링은 sample rate 변환을 통한 pitch shift로 여러 노트를 연주 가능하도록 오디오를 변환 `pydub, simpleaudio`
4. 키보드 입력을 통해 연주할 노트를 매핑하여 실제 연주가 가능
5. 연주할 때 음 높낮이에 따라 LED 디밍
6. (추가) GUI상에서 코드(Chord)를 정하고 들어볼 수 있는 기능

## 프로젝트 환경

🍓 라즈베리 파이 32bit에서 vscode로 진행

🍓 tkinter 때문에 ssh는 사용 불가

### 간단히 동작 요약

1. [samplePi.py](http://samplePi.py)를 실행하면 tkinter기반 GUI가 나타남
2. Load Sample 버튼을 통해 디렉토리에서 wav파일을 선택하여 로드
3. 로딩이 완료되면 버튼 옆에 선택한 파일 이름이 나오고 키보드 입력을 통해 연주가능
4. 4옥 도부터 6옥 솔까지 연주 가능
5. 4옥타브 건반 연주시 ⇒ 초록색 LED 디밍

   5옥타브 건반 연주시 ⇒ 노란색 LED 디밍

   6옥타브 건반 연주시 ⇒ 빨간색 LED 디밍

6. 동시에 연주하는 건반 갯수에 따라 더 밝아짐
7. Load sample 버튼을 통해 다른 프리셋으로 연주 가능!!
8. 코드(Chord)를 선택하고 버튼을 누르면 그에 맞는 5옥타브 코드를 연주해줌(디밍은 x)

## 사용한 라이브러리

1. `**Tkinter**`

   간단한 gui를 구현하기 위해 사용(버튼, 엔트리, 콤보박스)

2. `**pydub**`

   Pitch shift를 이용하여 음이 다른 오디오 샘플을 만들고 메모리에 저장을 해두는 데 쓰이는 오디오 라이브러리

   [GitHub - jiaaro/pydub: Manipulate audio with a simple and easy high level interface](https://github.com/jiaaro/pydub)

3. `**simpleaudio**`

   pydub은 멀티 스레딩 plaback을 지원하지 않는다. 따라서 키보드 입력 이벤트와 음악 재생이 동시에 이뤄질 수 있도록 해주는 라이브러리

   [Simpleaudio Package — simpleaudio 1.0.4 documentation](https://simpleaudio.readthedocs.io/en/latest/)
