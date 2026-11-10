
import json
from pathlib import Path
from capture import CaptureAnalyzer


def main():
    print("=" * 40)
    print("       TeaHack LOCO Analyzer")
    print("=" * 40)

    analyzer = CaptureAnalyzer()

    filename = input("분석할 캡처 파일: ").strip()

    try:
        result = analyzer.analyze(filename)

        print("\n[분석 결과]")
        print(json.dumps(
            result,
            ensure_ascii=False,
            indent=4,
            default=str
        ))

        output = Path("captures/result.json")
        output.parent.mkdir(exist_ok=True)

        output.write_text(
            json.dumps(
                result,
                ensure_ascii=False,
                indent=4,
                default=str
            ),
            encoding="utf-8"
        )

        print("\n분석 결과 저장 완료:", output)

    except Exception as error:
        print("\n분석 실패:", error)


if __name__ == "__main__":
    main()
