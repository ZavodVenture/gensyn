from __future__ import annotations

import argparse
import csv
import json
import traceback
import time
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
from urllib.error import URLError, HTTPError
from urllib.request import urlopen

URL_BASE = "https://dashboard-math.gensyn.ai/api/v1/peer?id={}"
TIMEOUT  = 10
RETRIES  = 3
BACKOFF  = 2


def load_peer_ids(file_path: Path) -> List[str]:
    """Возвращает список ID.  FileNotFoundError, если файла нет."""
    if not file_path.exists():
        raise FileNotFoundError(f"Файл {file_path} не найден.")
    with file_path.open(encoding="utf-8") as fh:
        return [
            line.strip()
            for line in fh
            if line.strip() and not line.lstrip().startswith("#")
        ]


def fetch_peer(peer_id: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    for attempt in range(1, RETRIES + 1):
        try:
            with urlopen(URL_BASE.format(peer_id), timeout=TIMEOUT) as resp:
                if resp.status != 200:
                    raise HTTPError(resp.geturl(), resp.status, resp.msg, resp.headers, None)
                data = json.loads(resp.read().decode())
            return str(data.get("score", "null")), str(data.get("reward", "null")), None
        except (URLError, HTTPError, json.JSONDecodeError, ValueError) as exc:
            if attempt == RETRIES:
                return None, None, str(exc)
            time.sleep(BACKOFF ** attempt)


def render_table(rows: List[Dict[str, Any]]) -> None:
    headers = ["Peer ID", "Score", "Reward", "Status"]
    data    = [[r["peer_id"], r["score"], r["reward"], r["status"]] for r in rows]
    widths  = [max(len(str(cell)) for cell in col) for col in zip(headers, *data)]

    def sep(char="-"):
        return "+" + "+".join(char * (w + 2) for w in widths) + "+"

    def line(cells):
        return "|" + "|".join(f" {c:<{w}} " for c, w in zip(cells, widths)) + "|"

    print(sep("="))
    print(line(headers))
    print(sep("="))
    for row in data:
        print(line([str(c) for c in row]))
    print(sep("="))


def main(file_path: str | Path = "peers.txt") -> None:
    peer_ids = load_peer_ids(Path(file_path))
    rows: List[Dict[str, Any]] = []

    total = len(peer_ids)
    for idx, pid in enumerate(peer_ids, 1):
        print(f"\rПроверяем {idx}/{total}…", end="", flush=True)
        score, reward, err = fetch_peer(pid)
        rows.append(
            {
                "peer_id": pid,
                "score":   score or "—",
                "reward":  reward or "—",
                "status":  "OK" if err is None else f"ERROR: {err}",
            }
        )
    print("\r" + " " * 40 + "\r", end="")  # очистка строки

    render_table(rows)

    with open("peer_results.csv", "w", newline="", encoding="utf-8") as fh:
        csv.DictWriter(fh, fieldnames=["peer_id", "score", "reward", "status"]).writeheader()
        csv.DictWriter(fh, fieldnames=["peer_id", "score", "reward", "status"]).writerows(rows)

    print("\nГотово! Результаты сохранены в peer_results.csv")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Проверка Gensyn peer-IDs (без внешних пакетов)"
    )
    parser.add_argument(
        "file",
        nargs="?",
        default="peers.txt",
        help="Текстовый файл с peer-ID (по одному в строке)",
    )

    try:
        main(parser.parse_args().file)
    except Exception:
        print("\nПроизошла ошибка:")
        traceback.print_exc()
    finally:
        input("\nНажмите Enter, чтобы закрыть окно…")
