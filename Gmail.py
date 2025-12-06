"""
Gmail APIを使ってメールを送信するプログラム
=============================================
使い方: python send_mail.py
"""

import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ===== 設定（ここを変更してください） =====

# 送信先のメールアドレス
TO_EMAIL = "tm.3112117@icloud.com"

# メールの件名
SUBJECT = "テストメール"

# メールの本文
BODY = """
こんにちは！

これはGmail APIを使って送信したテストメールです。

よろしくお願いします。
"""

# ==========================================

# 認証ファイルの設定
CREDENTIALS_FILE = "credentials.json"  # Google Cloud Consoleからダウンロードしたファイル
TOKEN_FILE = "token.json"              # 認証後に自動作成されるファイル

# Gmail APIの権限（メール送信）
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def get_credentials():
    """
    Googleの認証情報を取得する
    初回はブラウザでログインが必要、2回目以降は自動
    """
    creds = None
    
    # 以前の認証情報があれば読み込む
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # 認証情報がないか期限切れの場合
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # 期限切れなら更新
            print("認証情報を更新中...")
            creds.refresh(Request())
        else:
            # 新規認証（ブラウザが開く）
            if not os.path.exists(CREDENTIALS_FILE):
                print(f"エラー: {CREDENTIALS_FILE} が見つかりません")
                print("Google Cloud Consoleからダウンロードして、このフォルダに置いてください")
                return None
            
            print("ブラウザが開きます。Googleアカウントでログインしてください...")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # 認証情報を保存
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
        print("認証情報を保存しました")
    
    return creds


def create_message(to, subject, body):
    """メールを作成する"""
    message = MIMEMultipart()
    message["to"] = to
    message["subject"] = subject
    message.attach(MIMEText(body, "plain", "utf-8"))
    
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    return {"raw": raw}


def send_mail(to, subject, body):
    """メールを送信する"""
    print("=" * 50)
    print("Gmail メール送信")
    print("=" * 50)
    
    # 認証
    print("\n[1] 認証中...")
    creds = get_credentials()
    if not creds:
        return False
    print("    OK")
    
    # Gmail APIに接続
    print("[2] Gmail APIに接続中...")
    service = build("gmail", "v1", credentials=creds)
    print("    OK")
    
    # メール作成
    print("[3] メール作成中...")
    message = create_message(to, subject, body)
    print(f"    宛先: {to}")
    print(f"    件名: {subject}")
    print("    OK")
    
    # 送信
    print("[4] 送信中...")
    try:
        result = service.users().messages().send(userId="me", body=message).execute()
        print("    OK")
        print(f"\n送信完了！ (ID: {result['id']})")
        print("=" * 50)
        return True
    except Exception as e:
        print(f"    エラー: {e}")
        print("=" * 50)
        return False


if __name__ == "__main__":
    # 送信先が設定されているか確認
    if TO_EMAIL == "送信先のメールアドレス":
        print("=" * 50)
        print("送信先を設定してください")
        print("=" * 50)
        print("\nsend_mail.py を開いて TO_EMAIL を変更してください")
        print('例: TO_EMAIL = "example@gmail.com"')
        print("=" * 50)
    else:
        send_mail(TO_EMAIL, SUBJECT, BODY)

