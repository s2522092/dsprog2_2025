import requests
import json
from datetime import datetime

class WeatherAPIClient:
    def __init__(self):
        # 複数のエンドポイントを保持
        self.forecast_url = "https://www.jma.go.jp/bosai/forecast/data/forecast/"
        self.overview_url = "https://www.jma.go.jp/bosai/forecast/data/overview_forecast/"
        
    def get_weather(self, area_id):
        """気象庁APIから天気予報データを取得"""
        try:
            # まず従来のエンドポイントを試す
            url = f"http://www.jma.go.jp/bosai/forecast/data/forecast/{area_id}.json"
            print(f"APIリクエスト1: {url}")
            
            response = requests.get(url, timeout=10)
            
            # 失敗した場合は別のエンドポイントを試す
            if response.status_code != 200:
                print(f"最初のエンドポイントが失敗しました。別のエンドポイントを試します。")
                # 地域コードの最初の2桁を使用
                area_prefix = area_id[:2]
                url2 = f"{self.overview_url}{area_prefix}.json"
                print(f"APIリクエスト2: {url2}")
                
                response = requests.get(url2, timeout=10)
                
                # さらに失敗した場合、別の形式も試す
                if response.status_code != 200:
                    url3 = f"{self.overview_url}{area_id}.json"
                    print(f"APIリクエスト3: {url3}")
                    response = requests.get(url3, timeout=10)
            
            print(f"ステータスコード: {response.status_code}")
            if response.status_code != 200:
                print(f"エラーレスポンス: {response.text[:200]}")
                return None
                
            # 成功した場合はJSONを返す
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"API接続エラー: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"レスポンスステータス: {e.response.status_code}")
                print(f"レスポンス内容: {e.response.text[:200]}")
            return None
    
    def parse_weather_data(self, json_data, area_id):
        """APIレスポンスを解析して必要なデータを抽出"""
        if not json_data:
            return []
            
        # APIのレスポンス形式によって処理を分岐
        forecasts = []
        
        try:
            # 従来のフォーマットを試す
            if isinstance(json_data, list) and len(json_data) > 0:
                # 従来のフォーマット
                forecast_data = json_data[0]
                
                # エリア名を取得
                area_name = forecast_data["timeSeries"][0]["areas"][0]["area"]["name"]
                
                # 天気コードと天気テキスト
                weathers = forecast_data["timeSeries"][0]["areas"][0]["weatherCodes"]
                weather_texts = forecast_data["timeSeries"][0]["areas"][0]["weathers"]
                
                # 最高・最低気温
                try:
                    temps = forecast_data["timeSeries"][2]["areas"][0]["temps"]
                    min_temps = [temps[i] if i % 2 == 0 else None for i in range(len(temps))]
                    max_temps = [temps[i] if i % 2 == 1 else None for i in range(len(temps))]
                except (IndexError, KeyError):
                    min_temps = [None] * len(weathers)
                    max_temps = [None] * len(weathers)
                
                # 降水確率
                try:
                    rain_probs = forecast_data["timeSeries"][1]["areas"][0]["pops"]
                except (IndexError, KeyError):
                    rain_probs = [None] * len(weathers)
                    
                # 日付
                dates = forecast_data["timeSeries"][0]["timeDefines"]
                
                # データを結合
                for i in range(len(weathers)):
                    date_str = datetime.fromisoformat(dates[i].replace('Z', '+00:00')).strftime('%Y-%m-%d')
                    
                    forecast = {
                        "area_id": area_id,
                        "area_name": area_name,
                        "forecast_date": date_str,
                        "weather_code": weathers[i],
                        "weather_text": weather_texts[i],
                        "temperature_min": min_temps[i] if i < len(min_temps) and min_temps[i] != "" else None,
                        "temperature_max": max_temps[i] if i < len(max_temps) and max_temps[i] != "" else None,
                        "rainfall_probability": rain_probs[i] if i < len(rain_probs) and rain_probs[i] != "" else None
                    }
                    
                    forecasts.append(forecast)
            
            # 新しいフォーマットの場合
            elif "targetArea" in json_data and "text" in json_data:
                # 新しいフォーマット（overview_forecast形式）
                area_name = json_data.get("targetArea", "不明")
                forecast_text = json_data.get("text", "情報がありません")
                report_date = json_data.get("reportDatetime", "")
                
                if report_date:
                    date_obj = datetime.fromisoformat(report_date.replace('Z', '+00:00'))
                    date_str = date_obj.strftime('%Y-%m-%d')
                else:
                    date_str = datetime.now().strftime('%Y-%m-%d')
                
                forecast = {
                    "area_id": area_id,
                    "area_name": area_name,
                    "forecast_date": date_str,
                    "weather_code": "000",  # 代替コード
                    "weather_text": forecast_text,
                    "temperature_min": None,
                    "temperature_max": None,
                    "rainfall_probability": None
                }
                
                forecasts.append(forecast)
        
        except Exception as e:
            print(f"天気データの解析エラー: {e}")
            print(f"JSON形式: {json_data}")
        
        return forecasts