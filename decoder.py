
import struct
from bson import BSON
from bson.errors import InvalidBSON


HEADER_SIZE = 22
MAX_PACKET_SIZE = 10 * 1024 * 1024


class LocoDecoder:

    @staticmethod
    def decode(data: bytes):
        if len(data) < HEADER_SIZE:
            raise ValueError("헤더가 완성되지 않았습니다.")

        packet_id = struct.unpack_from("<i", data, 0)[0]
        status = struct.unpack_from("<h", data, 4)[0]

        method = data[6:17].split(b"\x00")[0]
        body_type = data[17]
        body_length = struct.unpack_from("<i", data, 18)[0]

        if not 0 <= body_length <= MAX_PACKET_SIZE:
            raise ValueError("잘못된 본문 크기")

        payload = data[HEADER_SIZE:]

        if len(payload) != body_length:
            raise ValueError("본문 길이가 일치하지 않습니다.")

        body = None

        if payload:
            if body_length < 5:
                raise ValueError("잘못된 BSON 길이")

            declared_length = struct.unpack("<i", payload[:4])[0]

            if declared_length != body_length:
                raise ValueError("BSON 길이 불일치")

            body = BSON(payload).decode()

        return {
            "packet_id": packet_id,
            "status": status,
            "method": method.decode("ascii", errors="replace"),
            "body_type": body_type,
            "body_length": body_length,
            "body": body
        }
