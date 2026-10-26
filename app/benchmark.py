"""第1回 宿題（発展）: 応答時間とトークン数を、複数のモデル・質問で繰り返し計測する。

使い方:
    uv run python -m app.benchmark
    uv run python -m app.benchmark --models gemini-3.5-flash-lite --repeat 5

結果は lectures/01/benchmark.csv に追記する（APIキーは書かない）。
"""

import argparse
import csv
import time
from datetime import datetime
from pathlib import Path

from google import genai
from google.genai import errors

from app.config import get_api_key

QUESTIONS = [
    "LoRAとは何ですか？",
    "AIE2026の講座の宿題にある「3レベル」とは何ですか？",
]
OUTPUT = Path("lectures/01/benchmark.csv")


def measure(client, model, question):
    """1回だけ質問し、(状態, 入力トークン数, 出力トークン数, 秒数) を返す。"""
    start = time.perf_counter()
    try:
        response = client.models.generate_content(model=model, contents=question)
    except errors.APIError as e:
        return f"error_{e.code}", None, None, time.perf_counter() - start
    elapsed = time.perf_counter() - start
    usage = response.usage_metadata
    return "ok", usage.prompt_token_count, usage.candidates_token_count, elapsed


def main():
    parser = argparse.ArgumentParser(description="応答時間とトークン数を計測する")
    parser.add_argument("--models", nargs="+", default=["gemini-3.5-flash-lite", "gemini-3.8-flash"])
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--sleep", type=float, default=13.0, help="呼び出しの間に待つ秒数")
    args = parser.parse_args()

    client = genai.Client(api_key=get_api_key())
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    is_new = not OUTPUT.exists()

    with OUTPUT.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if is_new:
            writer.writerow(["timestamp", "model", "question", "trial", "status",
                             "input_tokens", "output_tokens", "elapsed_sec"])
        for model in args.models:
            for question in QUESTIONS:
                for trial in range(1, args.repeat + 1):
                    status, inp, out, elapsed = measure(client, model, question)
                    writer.writerow([datetime.now().isoformat(timespec="seconds"), model, question,
                                     trial, status, inp, out, f"{elapsed:.2f}"])
                    f.flush()
                    print(f"{model} | {question[:12]}… | {trial}回目 | {status} | "
                          f"入力 {inp} / 出力 {out} | {elapsed:.2f} 秒")
                    time.sleep(args.sleep)


if __name__ == "__main__":
    main()