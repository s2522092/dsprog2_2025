"""
気象庁API天気予報アプリケーション (Flet版)
"""
import flet as ft
from api import JMAWeatherAPI
from datetime import datetime
from typing import Optional, List, Dict


class WeatherForecastApp:
    """天気予報アプリケーションクラス"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "気象庁 天気予報アプリ"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 20
        
        # データ
        self.area_data = None
        self.areas = []
        self.selected_area_code = None
        
        # UI コンポーネント
        self.area_dropdown = None
        self.get_weather_btn = None
        self.loading_indicator = None
        self.error_text = None
        self.weather_container = None
        
        # 初期化
        self.setup_ui()
        self.load_area_list()
    
    def setup_ui(self):
        """UIのセットアップ"""
        
        # ヘッダー
        header = ft.Container(
            content=ft.Column([
                ft.Text(
                    "🌤️ 天気予報アプリ",
                    size=32,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.WHITE,
                ),
                ft.Text(
                    "気象庁データを利用した天気予報",
                    size=16,
                    color=ft.colors.WHITE70,
                ),
            ]),
            bgcolor=ft.colors.BLUE_700,
            padding=30,
            border_radius=10,
            margin=ft.margin.only(bottom=20),
        )
        
        # 地域選択セクション
        self.area_dropdown = ft.Dropdown(
            label="地域を選択",
            hint_text="地域を選択してください",
            width=400,
            disabled=True,
            on_change=self.on_area_changed,
        )
        
        self.get_weather_btn = ft.ElevatedButton(
            "天気予報を取得",
            icon=ft.icons.CLOUD,
            on_click=self.on_get_weather_clicked,
            disabled=True,
            width=400,
            height=50,
        )
        
        area_selection = ft.Container(
            content=ft.Column([
                ft.Text("地域を選択してください", size=20, weight=ft.FontWeight.BOLD),
                self.area_dropdown,
                self.get_weather_btn,
            ], spacing=15),
            bgcolor=ft.colors.GREY_100,
            padding=20,
            border_radius=10,
            margin=ft.margin.only(bottom=20),
        )
        
        # ローディングインジケーター
        self.loading_indicator = ft.Container(
            content=ft.Column([
                ft.ProgressRing(),
                ft.Text("データを取得中...", size=16),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            visible=False,
            padding=20,
        )
        
        # エラーメッセージ
        self.error_text = ft.Container(
            content=ft.Text("", color=ft.colors.RED_700, size=16),
            visible=False,
            bgcolor=ft.colors.RED_50,
            padding=15,
            border_radius=8,
            border=ft.border.all(2, ft.colors.RED_200),
            margin=ft.margin.only(bottom=20),
        )
        
        # 天気予報表示エリア
        self.weather_container = ft.Container(
            content=ft.Column([], spacing=15),
            visible=False,
        )
        
        # フッター
        footer = ft.Container(
            content=ft.Row([
                ft.Text("データ提供: ", size=14),
                ft.TextButton(
                    "気象庁",
                    url="https://www.jma.go.jp/",
                ),
            ], alignment=ft.MainAxisAlignment.CENTER),
            bgcolor=ft.colors.GREY_100,
            padding=15,
            border_radius=10,
            margin=ft.margin.only(top=20),
        )
        
        # ページに追加
        self.page.add(
            ft.SafeArea(
                ft.Column([
                    header,
                    area_selection,
                    self.loading_indicator,
                    self.error_text,
                    self.weather_container,
                    footer,
                ], scroll=ft.ScrollMode.AUTO),
                expand=True,
            )
        )
    
    def load_area_list(self):
        """地域リストを読み込む"""
        self.show_loading(True)
        self.hide_error()
        
        # APIから地域リストを取得
        self.area_data = JMAWeatherAPI.fetch_area_list()
        
        if self.area_data:
            self.areas = JMAWeatherAPI.format_area_data(self.area_data)
            self.populate_area_dropdown()
            self.show_loading(False)
        else:
            self.show_loading(False)
            self.show_error("地域リストの取得に失敗しました。")
    
    def populate_area_dropdown(self):
        """ドロップダウンに地域を追加"""
        self.area_dropdown.options = [
            ft.dropdown.Option(key=area["code"], text=area["name"])
            for area in self.areas
        ]
        self.area_dropdown.disabled = False
        self.area_dropdown.update()
    
    def on_area_changed(self, e):
        """地域選択時の処理"""
        self.selected_area_code = self.area_dropdown.value
        self.get_weather_btn.disabled = not bool(self.selected_area_code)
        self.get_weather_btn.update()
    
    def on_get_weather_clicked(self, e):
        """天気予報取得ボタンクリック時の処理"""
        if not self.selected_area_code:
            self.show_error("地域を選択してください。")
            return
        
        self.load_weather_forecast()
    
    def load_weather_forecast(self):
        """天気予報を読み込む"""
        self.show_loading(True)
        self.hide_error()
        self.hide_weather_display()
        
        # APIから天気予報を取得
        forecast_data = JMAWeatherAPI.fetch_weather_forecast(self.selected_area_code)
        
        if forecast_data:
            self.display_weather_forecast(forecast_data)
            self.show_loading(False)
        else:
            self.show_loading(False)
            self.show_error("天気予報の取得に失敗しました。")
    
    def display_weather_forecast(self, data: List[Dict]):
        """天気予報を表示"""
        if not data or len(data) == 0:
            self.show_error("天気予報データが見つかりませんでした。")
            return
        
        forecast = data[0]
        selected_area_name = next(
            (area["name"] for area in self.areas if area["code"] == self.selected_area_code),
            "不明"
        )
        
        # コンテンツをクリア
        self.weather_container.content.controls.clear()
        
        # タイトル
        title = ft.Text(
            f"{selected_area_name}の天気予報",
            size=24,
            weight=ft.FontWeight.BOLD,
        )
        
        # 発表情報
        info_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.icons.BUSINESS, color=ft.colors.BLUE_700),
                        ft.Text(f"発表元 {forecast.get('publishingOffice', '不明')}", size=14),
                    ]),
                    ft.Row([
                        ft.Icon(ft.icons.ACCESS_TIME, color=ft.colors.BLUE_700),
                        ft.Text(
                            f"発表日時 {self.format_datetime(forecast.get('reportDatetime'))}",
                            size=14
                        ),
                    ]),
                ], spacing=10),
                padding=15,
            ),
        )
        
        self.weather_container.content.controls.extend([title, info_card])
        
        # 時系列データを表示
        if "timeSeries" in forecast:
            for index, series in enumerate(forecast["timeSeries"]):
                card = self.create_time_series_card(series, index)
                self.weather_container.content.controls.append(card)
        
        self.show_weather_display()
    
    def create_time_series_card(self, series: Dict, index: int) -> ft.Card:
        """時系列カードを作成"""
        titles = ["天気予報", "降水確率・気温", "週間予報"]
        title = titles[index] if index < len(titles) else f"予報 {index + 1}"
        
        card_content = ft.Column([
            ft.Container(
                content=ft.Text(title, size=18, weight=ft.FontWeight.BOLD),
                bgcolor=ft.colors.BLUE_50,
                padding=10,
                border_radius=ft.border_radius.only(top_left=10, top_right=10),
            ),
        ], spacing=0)
        
        time_defines = series.get("timeDefines", [])
        areas = series.get("areas", [])
        
        if areas:
            area = areas[0]
            
            for time_index, time in enumerate(time_defines):
                forecast_item = self.create_forecast_item(area, time_index, time)
                card_content.controls.append(forecast_item)
        
        return ft.Card(
            content=ft.Container(
                content=card_content,
                padding=0,
            ),
            elevation=3,
        )
    
    def create_forecast_item(self, area: Dict, index: int, time: str) -> ft.Container:
        """予報アイテムを作成"""
        details = []
        
        # 時刻ヘッダー
        details.append(
            ft.Container(
                content=ft.Text(
                    self.format_datetime(time),
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.BLUE_700,
                ),
                margin=ft.margin.only(bottom=8),
            )
        )
        
        # 各種情報を追加
        info_items = []
        
        if "weatherCodes" in area and index < len(area["weatherCodes"]):
            info_items.append(("天気コード", area["weatherCodes"][index]))
        
        if "weathers" in area and index < len(area["weathers"]):
            info_items.append(("天気", area["weathers"][index]))
        
        if "winds" in area and index < len(area["winds"]):
            info_items.append(("風", area["winds"][index]))
        
        if "waves" in area and index < len(area["waves"]):
            info_items.append(("波", area["waves"][index]))
        
        if "pops" in area and index < len(area["pops"]):
            info_items.append(("降水確率", f"{area['pops'][index]}%"))
        
        if "temps" in area and index < len(area["temps"]):
            info_items.append(("気温", f"{area['temps'][index]}°C"))
        
        # 情報行を作成
        for label, value in info_items:
            if value:
                details.append(
                    ft.Row([
                        ft.Text(f"{label}", size=14, weight=ft.FontWeight.W_500, width=100),
                        ft.Text(str(value), size=14),
                    ], spacing=10)
                )
        
        return ft.Container(
            content=ft.Column(details, spacing=5),
            bgcolor=ft.colors.GREY_50,
            padding=15,
            margin=ft.margin.only(left=10, right=10, bottom=10),
            border_radius=8,
            border=ft.border.all(1, ft.colors.GREY_300),
        )
    
    def format_datetime(self, datetime_str: Optional[str]) -> str:
        """日時をフォーマット"""
        if not datetime_str:
            return "不明"
        
        try:
            dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            return dt.strftime("%Y年%m月%d日 %H:%M")
        except Exception:
            return datetime_str
    
    def show_loading(self, show: bool):
        """ローディング表示の切り替え"""
        self.loading_indicator.visible = show
        self.loading_indicator.update()
    
    def show_error(self, message: str):
        """エラーメッセージを表示"""
        self.error_text.content.value = message
        self.error_text.visible = True
        self.error_text.update()
    
    def hide_error(self):
        """エラーメッセージを非表示"""
        self.error_text.visible = False
        self.error_text.update()
    
    def show_weather_display(self):
        """天気予報表示を表示"""
        self.weather_container.visible = True
        self.weather_container.update()
    
    def hide_weather_display(self):
        """天気予報表示を非表示"""
        self.weather_container.visible = False
        self.weather_container.update()


def main(page: ft.Page):
    """メイン関数"""
    WeatherForecastApp(page)


if __name__ == "__main__":
    ft.app(target=main)