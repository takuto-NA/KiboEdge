"""
責務: LM Studio の OpenAI 互換 API に対してメッセージを送信し、応答を受信する。
ローカルで起動した LM Studio (http://127.0.0.1:1234) とチャットのやり取りを行う。
"""

import os
from openai import OpenAI


# 定数（マジックナンバー禁止）
LMSTUDIO_BASE_URL = "http://127.0.0.1:1234/v1"
LMSTUDIO_MODEL_NAME = "lfm2-8b-a1b"
DEFAULT_API_KEY = "lm-studio"  # ローカル LM Studio はキー不要だが互換のため指定


def create_lmstudio_client() -> OpenAI:
    """LM Studio の OpenAI 互換エンドポイント用のクライアントを生成する。"""
    return OpenAI(
        base_url=LMSTUDIO_BASE_URL,
        api_key=os.environ.get("LMSTUDIO_API_KEY", DEFAULT_API_KEY),
    )


def send_message_and_get_reply(client: OpenAI, user_message: str) -> str:
    """
    ユーザーメッセージを送信し、モデルからの応答テキストを返す。
    応答が取得できない場合は空文字を返す。
    """
    response = client.chat.completions.create(
        model=LMSTUDIO_MODEL_NAME,
        messages=[{"role": "user", "content": user_message}],
        max_tokens=512,
    )
    first_choice = response.choices[0] if response.choices else None
    if first_choice is None:
        return ""
    return first_choice.message.content or ""


def main() -> None:
    """LM Studio に挨拶メッセージを送り、応答を表示する。"""
    client = create_lmstudio_client()
    greeting = "こんにちは。短く自己紹介してください。"
    print(f"送信: {greeting}")
    reply = send_message_and_get_reply(client, greeting)
    print(f"応答: {reply}")


if __name__ == "__main__":
    main()
