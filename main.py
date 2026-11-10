
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path


class TeaHackAnalyzer:

    def __init__(self):
        self.output = Path("captures")
        self.output.mkdir(exist_ok=True)

        self.packet_count = 0
        self.total_bytes = 0

    def analyze(self, data):

        self.packet_count += 1
        self.total_bytes += len(data)

        result = {
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),

            "packet_number": self.packet_count,
            "size": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "preview": data[:64].hex()
        }

        print(json.dumps(
            result,
            ensure_ascii=False,
            indent=4
        ))

        with open(
            self.output / "live.jsonl",
            "a",
            encoding="utf-8"
        ) as file:
            file.write(
                json.dumps(result, ensure_ascii=False) + "\n"
            )

    def start(self):

        print("=" * 40)
        print("       TeaHack LOCO Analyzer")
        print("=" * 40)

        print("1. HEX 패킷 분석")
        print("2. 분석 통계")
        print("3. 종료")

        while True:

            choice = input("\n선택 > ").strip()

            if choice == "1":

                try:
                    raw = bytes.fromhex(
                        input("HEX 데이터 > ")
                    )
                    self.analyze(raw)

                except ValueError as error:
                    print("오류:", error)

            elif choice == "2":

                print("패킷 수:", self.packet_count)
                print("전체 데이터:", self.total_bytes, "bytes")

            elif choice == "3":
                print("TeaHack 종료")
                break

            else:
                print("잘못된 명령어")


if __name__ == "__main__":
    TeaHackAnalyzer().start()
