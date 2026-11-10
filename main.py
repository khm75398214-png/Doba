
import socket
import struct
from pathlib import Path
from datetime import datetime
import time

HOST = "127.0.0.1"
PORT = 1234
MAX_PACKET = 16 * 1024 * 1024

OUTPUT = Path("captures")
OUTPUT.mkdir(exist_ok=True)


def receive_exact(sock, size):
    data = bytearray()

    while len(data) < size:
        chunk = sock.recv(size - len(data))

        if not chunk:
            if not data:
                return None
            raise ConnectionError("연결이 중간에 종료됨")

        data.extend(chunk)

    return bytes(data)


def detect_endian(header):
    magic = header[:4]

    formats = {
        b"\xd4\xc3\xb2\xa1": "<",
        b"\xa1\xb2\xc3\xd4": ">",
        b"\x4d\x3c\xb2\xa1": "<",
        b"\xa1\xb2\x3c\x4d": ">"
    }

    return formats.get(magic)


def handle_client(conn, address):
    filename = OUTPUT / (
        "live_" +
        datetime.now().strftime("%Y%m%d_%H%M%S") +
        ".pcap"
    )

    print("\n[+] 연결:", address)

    try:
        with filename.open("wb") as file:

            global_header = receive_exact(conn, 24)

            if global_header is None:
                return

            endian = detect_endian(global_header)

            if endian is None:
                raise ValueError("잘못된 PCAP 헤더")

            file.write(global_header)
            file.flush()

            packet_count = 0
            total_bytes = 0

            print("[+] PCAP 스트림 수신 시작")

            while True:
                record = receive_exact(conn, 16)

                if record is None:
                    break

                included = struct.unpack(
                    endian + "I",
                    record[8:12]
                )[0]

                original = struct.unpack(
                    endian + "I",
                    record[12:16]
                )[0]

                if included > MAX_PACKET:
                    raise ValueError("패킷 크기 초과")

                payload = receive_exact(conn, included)

                if payload is None:
                    break

                file.write(record)
                file.write(payload)
                file.flush()

                packet_count += 1
                total_bytes += included

                print(
                    f"[PACKET {packet_count}] "
                    f"저장={included} bytes "
                    f"원본길이={original} bytes "
                    f"누적={total_bytes} bytes"
                )

        print("[+] 저장 완료:", filename)

    except Exception as error:
        print("[-] 오류:", error)


def main():
    print("=" * 42)
    print("       TeaHack Live Analyzer")
    print("=" * 42)
    print("수신 주소:", HOST)
    print("포트:", PORT)
    print("종료: CTRL + C")

    server = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    server.bind((HOST, PORT))
    server.listen(5)

    try:
        while True:
            conn, address = server.accept()

            with conn:
                handle_client(conn, address)

    except KeyboardInterrupt:
        print("\n분석기 종료")

    finally:
        server.close()


if __name__ == "__main__":
    main()
