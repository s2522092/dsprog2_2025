# 天気予報アプリケーション（DB版）

気象庁APIからデータを取得し、SQLiteデータベースに保存して表示する天気予報アプリケーションです。

## 機能

- 気象庁APIからの天気予報データの取得
- SQLiteデータベースへのデータ保存
- エリア選択による天気予報表示
- データ更新機能
- （オプション）過去の予報データ閲覧機能

## 技術スタック

- Python
- Flet (UI)
- SQLite (データベース)
- requests (API通信)

## データベース設計

### エリアテーブル (areas)
エリア情報を管理するテーブル
- area_id: テキスト (主キー) - 気象庁API用のエリアID
- area_name: テキスト - エリア名
- region: テキスト - 地方名（例: 関東、九州）
- display_order: 整数 - 表示順

### 天気予報テーブル (weather_forecasts)
天気予報データを格納するテーブル
- id: 整数 (主キー、自動採番)
- area_id: テキスト (外部キー) - 対象エリアID
- forecast_date: テキスト - 予報日 (YYYY-MM-DD形式)
- weather_code: テキスト - 天気コード
- weather_text: テキスト - 天気の説明文
- temperature_min: 実数 - 最低気温
- temperature_max: 実数 - 最高気温
- rainfall_probability: 整数 - 降水確率(%)
- fetch_timestamp: テキスト - データ取得日時

## 使用方法

1. アプリを起動する