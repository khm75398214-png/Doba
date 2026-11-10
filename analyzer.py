
import json
import socket
import hashlib
from datetime import datetime, timezone
from pathlib import Path


class TeaHackAnalyzer:

    def __init__(self):
        self.output = Path("captures")
        self.output.mkdir(exist_ok=True)

        self.statistics = {
            "packets": 0,
            "bytes": 0
        }

    def analyze(self, data, source, destination):

        self.statistics["packets"] += 1
        self.statistics["bytes"] += len(data)

        result = {
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),

            "source": source,
            "destination": destination,

            "size": len(data),

            "sha256": hashlib.sha256(
                data
            ).hexdigest(),

            "preview": data[:32].hex()
        }

        print(json.dumps(
            result,
            ensure_ascii=False,
            indent=2
        ))

        self.save(result)

    def save(self, result):

        filename = self.output / "live.jsonl"

        with filename.open(
            "a",
            encoding="utf-8"
        ) as file:

            file.write(
                json.dumps(
                    result,
                    ensure_ascii=False
                ) + "\n"
            )


if __name__ == "__main__":

    analyzer = TeaHackAnalyzer()

    print("=== TeaHack Android Analyzer ===")
    print("로컬 테스트 데이터 분석 모드")

    while True:

        try:
            raw = bytes.fromhex(
                input("\nHEX 데이터 입력 > ")
            )

            analyzer.analyze(
                raw,
                "local",
                "test"
            )

        except KeyboardInterrupt:
            print("\n종료")
            break

        except ValueError as error:
            print("입력 오류:", error)
