
import json
import time
from datetime import datetime, timezone
from collections import defaultdict
from scapy.all import sniff, IP, TCP


class LocoMonitor:

    def __init__(self, target_ip=None):
        self.target_ip = target_ip
        self.connections = defaultdict(
            lambda: {
                "packets": 0,
                "bytes": 0,
                "first_seen": None,
                "last_seen": None
            }
        )

    def process_packet(self, packet):

        if IP not in packet or TCP not in packet:
            return

        ip = packet[IP]
        tcp = packet[TCP]

        if self.target_ip:
            if ip.src != self.target_ip and ip.dst != self.target_ip:
                return

        if tcp.dport not in (443, 995, 10009) and \
           tcp.sport not in (443, 995, 10009):
            return

        key = (
            ip.src,
            tcp.sport,
            ip.dst,
            tcp.dport
        )

        now = datetime.now(timezone.utc).isoformat()
        payload_size = len(bytes(tcp.payload))

        stats = self.connections[key]

        stats["packets"] += 1
        stats["bytes"] += len(packet)
        stats["last_seen"] = now

        if stats["first_seen"] is None:
            stats["first_seen"] = now

        result = {
            "timestamp": now,
            "source": f"{ip.src}:{tcp.sport}",
            "destination": f"{ip.dst}:{tcp.dport}",
            "flags": str(tcp.flags),
            "payload_size": payload_size,
            "connection_packets": stats["packets"],
            "connection_bytes": stats["bytes"]
        }

        print(json.dumps(
            result,
            ensure_ascii=False
        ))

    def start(self, interface=None):

        print("TeaHack Live Network Analyzer")
        print("실시간 패킷 관찰 시작")
        print("종료: Ctrl+C")

        try:
            sniff(
                iface=interface,
                filter="tcp",
                prn=self.process_packet,
                store=False
            )

        except KeyboardInterrupt:
            print("\n분석 종료")

        finally:
            self.export()

    def export(self):

        output = []

        for key, stats in self.connections.items():
            output.append({
                "connection": key,
                **stats
            })

        with open(
            "captures/live_report.json",
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                output,
                file,
                ensure_ascii=False,
                indent=4
            )

        print("분석 보고서 저장 완료")


if __name__ == "__main__":

    monitor = LocoMonitor()

    monitor.start()
