
from pathlib import Path
from decoder import LocoDecoder


class CaptureAnalyzer:

    def analyze(self, filename):
        data = Path(filename).read_bytes()

        if len(data) < 22:
            raise ValueError("캡처 데이터가 너무 짧습니다.")

        return LocoDecoder.decode(data)
