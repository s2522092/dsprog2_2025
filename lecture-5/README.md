# 気象庁API天気予報アプリケーション (Flet版)

Fletフレームワークを使用した気象庁API天気予報アプリケーションです。

## 機能

- 📍 日本全国の地域リストを取得・表示
- 🌤️ 選択した地域の詳細な天気予報を表示
- 📊 時系列ごとの予報情報
- 📱 クロスプラットフォーム対応（デスクトップ、Web、モバイル）

## 技術スタック

- **Flet**: Python UIフレームワーク
- **Requests**: HTTP通信ライブラリ
- **気象庁API**: 天気予報データ

## セットアップ

### 1. リポジトリのクローン

\`\`\`bash
git clone https://github.com/yourusername/weather-forecast-flet.git
cd weather-forecast-flet
\`\`\`

### 2. 仮想環境の作成（推奨）

\`\`\`bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
\`\`\`

### 3. 依存パッケージのインストール

\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 4. アプリケーションの実行

\`\`\`bash
# デスクトップアプリとして実行
python main.py

# Webアプリとして実行
flet run main.py --web
\`\`\`

## 使い方

1. アプリケーションが起動すると、自動的に地域リストが読み込まれます
2. ドロップダウンから地域を選択します
3. 「天気予報を取得」ボタンをクリックします
4. 選択した地域の天気予報が表示されます

## プロジェクト構成

\`\`\`
weather-forecast-flet/
├── README.md           # プロジェクト説明
├── main.py            # メインアプリケーション
├── api.py             # API通信処理
├── requirements.txt   # 依存パッケージ
└── .gitignore         # Git除外設定
\`\`\`

## GitHubフローでの開発

### ブランチ作成

\`\`\`bash
git checkout -b feature/ui-improvements
\`\`\`

### コミット

\`\`\`bash
git add .
git commit -m "feat: UI改善を実装"
\`\`\`

### プッシュ

\`\`\`bash
git push origin feature/ui-improvements
\`\`\`

### プルリクエスト

GitHubでプルリクエストを作成し、マージします。

## コミットメッセージ規約

- `feat:` 新機能追加
- `fix:` バグ修正
- `docs` ドキュメント更新
- `style:` コードスタイル修正
- `refactor:` リファクタリング
- `test:` テスト追加・修正
- `chore:` ビルド設定など

## ライセンス

MIT License

## データ提供

気象庁 (Japan Meteorological Agency)