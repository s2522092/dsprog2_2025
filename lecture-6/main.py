import flet as ft
import json
import os
from datetime import datetime, timedelta

from db import WeatherDatabase
from api_client import WeatherAPIClient

# 元の気象データJSONファイルのパス
AREA_JSON_PATH = "area.json"

class WeatherApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "天気予報アプリ"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.window_width = 800
        self.page.window_height = 600
        
        # データベースとAPIクライアントの初期化
        self.db = WeatherDatabase()
        self.api = WeatherAPIClient()
        
        # エリアデータの初期化（DBに登録）
        self.initialize_area_data()
        
        # UIコンポーネントの初期化
        self.setup_ui()
        
        # 初期データの読み込み
        self.load_initial_data()
        
    def initialize_area_data(self):
        """JSONファイルからエリアデータを読み込んでDBに登録"""
        # JSONファイルが存在すれば読み込む
        if os.path.exists(AREA_JSON_PATH):
            try:
                with open(AREA_JSON_PATH, 'r', encoding='utf-8') as f:
                    area_data = json.load(f)
                
                # エリアデータをDBに登録
                for region, areas in area_data.items():
                    for i, (area_id, area_name) in enumerate(areas.items()):
                        self.db.insert_area(area_id, area_name, region, i)
                        
                print("エリアデータをDBに登録しました")
            except Exception as e:
                print(f"エリアデータの読み込みエラー: {e}")
        else:
            print(f"エリアデータファイル {AREA_JSON_PATH} が見つかりません")
        
    def setup_ui(self):
        """UIコンポーネントの初期化"""
        # タイトル
        self.title = ft.Text("天気予報アプリ（DB版）", size=24, weight=ft.FontWeight.BOLD)
        
        # エリア選択ドロップダウン
        self.area_dropdown = ft.Dropdown(
            label="地域を選択",
            width=200,
        )
        # イベントハンドラを設定
        self.area_dropdown.on_change = self.on_area_changed
        
        # 更新ボタン
        self.update_button = ft.ElevatedButton(
            text="データ更新",
            icon="REFRESH"
        )
        self.update_button.on_click = self.on_update_clicked
        
        # 日付選択
        self.date_picker = ft.DatePicker(
            first_date=datetime.now() - timedelta(days=30),
            last_date=datetime.now() + timedelta(days=7),
            current_date=datetime.now()
        )
        
        self.date_button = ft.ElevatedButton(
            text="日付選択",
            icon="CALENDAR_TODAY"
        )
        self.date_button.on_click = lambda _: self.date_picker.pick_date()
        
        # 日付選択の結果を表示
        self.selected_date_text = ft.Text("すべての予報を表示中", italic=True)
        
        # 読み込み中表示
        self.loading = ft.ProgressBar(visible=False, width=300)
        
        # 天気表示エリア
        self.weather_cards = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
        
        # ステータスメッセージ
        self.status_text = ft.Text("", italic=True, size=12)
        
        # レイアウト
        self.page.add(
            ft.Column([
                self.title,
                ft.Row([
                    self.area_dropdown,
                    ft.Column([
                        ft.Row([
                            self.date_button,
                            self.selected_date_text
                        ]),
                        self.update_button
                    ])
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                self.loading,
                self.status_text,
                ft.Container(
                    content=self.weather_cards,
                    padding=10,
                    border_radius=8,
                    bgcolor=ft.Colors.BLUE_GREY_50,
                    expand=True
                )
            ], spacing=20, expand=True)
        )
        
        # DatePickerのイベントハンドラー設定
        self.page.overlay.append(self.date_picker)
        self.date_picker.on_result = self.on_date_changed
        
    def load_initial_data(self):
        """初期データの読み込み"""
        # DBからエリア一覧を取得
        areas = self.db.get_all_areas()
        
        # ドロップダウンにエリアを追加
        options = []
        for area in areas:
            options.append(ft.dropdown.Option(
                key=area["area_id"],
                text=f"{area['region']} - {area['area_name']}"
            ))
        
        self.area_dropdown.options = options
        
        # 最初のエリアを選択
        if options:
            self.area_dropdown.value = options[0].key
            self.page.update()
            self.on_area_changed(None)  # 選択時の処理を実行
        
    def on_area_changed(self, e):
        """エリア選択時の処理"""
        if not self.area_dropdown.value:
            return
            
        area_id = self.area_dropdown.value
        
        # DBから予報データを取得
        forecasts = self.db.get_forecast(area_id)
        
        # データがない場合はAPIから取得
        if not forecasts:
            self.status_text.value = "データをAPIから取得します..."
            self.page.update()
            self.fetch_and_store_weather(area_id)
        else:
            # 取得したデータを表示
            self.update_weather_display(forecasts)
        
    def on_update_clicked(self, e):
        """更新ボタンクリック時の処理"""
        if not self.area_dropdown.value:
            self.status_text.value = "エリアを選択してください"
            self.page.update()
            return
            
        area_id = self.area_dropdown.value
        
        # APIからデータを取得してDBに保存
        self.fetch_and_store_weather(area_id)

    def on_date_changed(self, e):
        """日付選択時の処理"""
        if e.date is None:
            self.selected_date_text.value = "すべての予報を表示中"
            self.page.update()
            
            # すべての予報を表示
            if self.area_dropdown.value:
                forecasts = self.db.get_forecast(self.area_dropdown.value)
                self.update_weather_display(forecasts)
            return
        
        # 選択された日付を文字列に変換
        selected_date = e.date.strftime('%Y-%m-%d')
        self.selected_date_text.value = f"選択日: {selected_date}"
        self.page.update()
        
        # 選択された日付の予報を表示
        if self.area_dropdown.value:
            forecasts = self.db.get_forecast(self.area_dropdown.value, selected_date)
            self.update_weather_display(forecasts)
        
    def fetch_and_store_weather(self, area_id):
        """APIからデータを取得してDBに保存"""
        self.loading.visible = True
        self.page.update()
        
        # APIからデータ取得
        json_data = self.api.get_weather(area_id)
        
        if not json_data:
            self.status_text.value = "データの取得に失敗しました"
            self.loading.visible = False
            self.page.update()
            return
            
        # データをパース
        forecasts = self.api.parse_weather_data(json_data, area_id)
        
        # DBに保存
        for forecast in forecasts:
            self.db.insert_forecast(
                forecast["area_id"],
                forecast["forecast_date"],
                forecast["weather_code"],
                forecast["weather_text"],
                forecast["temperature_min"],
                forecast["temperature_max"],
                forecast["rainfall_probability"]
            )
        
        # 取得したデータを表示
        self.update_weather_display(forecasts)
        
        self.loading.visible = False
        self.status_text.value = f"データを更新しました（{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}）"
        self.page.update()
        
    def update_weather_display(self, forecasts):
        """天気予報表示の更新"""
        self.weather_cards.controls.clear()
        
        if not forecasts:
            self.weather_cards.controls.append(
                ft.Text("データがありません。更新ボタンを押してください。")
            )
            self.page.update()
            return
            
        # 地域名を表示
        area_name = forecasts[0].get("area_name", "不明")
        self.weather_cards.controls.append(
            ft.Text(f"{area_name}の天気予報", size=20, weight=ft.FontWeight.BOLD)
        )
        
        # 各日の予報を表示
        for forecast in forecasts:
            date = forecast["forecast_date"]
            weather = forecast["weather_text"]
            temp_min = forecast["temperature_min"]
            temp_max = forecast["temperature_max"]
            rain_prob = forecast["rainfall_probability"]
            
            # 日付フォーマット
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            date_str = date_obj.strftime('%m/%d') + f"({['月','火','水','木','金','土','日'][date_obj.weekday()]})"
            
            # 天気アイコン（簡易版）
            weather_icon = "SUNNY"  # デフォルト
            if "雨" in weather:
                weather_icon = "UMBRELLA"
            elif "曇" in weather:
                weather_icon = "CLOUD"
                
            # カード作成
            card = ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.ListTile(
                            leading=ft.Icon(weather_icon),
                            title=ft.Text(f"{date_str}: {weather}"),
                            subtitle=ft.Text(
                                f"気温: {temp_min or '?'}℃～{temp_max or '?'}℃  降水確率: {rain_prob or '?'}%"
                            )
                        )
                    ]),
                    padding=10
                )
            )
            
            self.weather_cards.controls.append(card)
            
        self.page.update()

def main(page: ft.Page):
    """アプリケーションのエントリーポイント"""
    app = WeatherApp(page)

if __name__ == "__main__":
    ft.app(target=main)