"""GuitarSet 주석 파일(annotation.zip, 약 40MB)만 내려받아 data/guitarset/annotation/ 에 푼다.
오디오는 필요 없다 (이 프로젝트는 '어떤 음을 어느 줄에서 쳤는가'만 쓴다).

출처: Xi et al., "GuitarSet: A Dataset for Guitar Transcription", ISMIR 2018 (CC BY 4.0)
"""
import os
import urllib.request
import zipfile

URL = "https://zenodo.org/record/3371780/files/annotation.zip?download=1"
DEST = os.path.join("data", "guitarset")


def main():
    os.makedirs(DEST, exist_ok=True)
    zip_path = os.path.join(DEST, "annotation.zip")
    if not os.path.exists(zip_path):
        print("다운로드 중...", URL)
        urllib.request.urlretrieve(URL, zip_path)
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(os.path.join(DEST, "annotation"))
    n = sum(f.endswith(".jams") for _, _, fs in os.walk(DEST) for f in fs)
    print(f"완료: .jams 파일 {n}개 (정상이라면 360개)")


if __name__ == "__main__":
    main()
