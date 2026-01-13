"""
気象庁API関連の処理
"""
import requests
from typing import Dict, List, Optional


class JMAWeatherAPI:
    """気象庁APIクラス"""
    
    AREA_LIST_URL = "https://www.jma.go.jp/bosai/common/const/area.json"
    FORECAST_URL = "https://www.jma.go.jp/bosai/forecast/data/forecast/"
    
    @staticmethod
    def fetch_area_list() -> Optional[Dict]:
        """
        地域リストを取得
        
        Returns:
            Dict 地域データ、失敗時はNone
        """
        try:
            response = requests.get(JMAWeatherAPI.AREA_LIST_URL, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"地域リスト取得エラー: {e}")
            return None
    
    @staticmethod
    def fetch_weather_forecast(area_code: str) -> Optional[Dict]:
        """
        指定地域の天気予報を取得
        
        Args:
            area_code: 地域コード
            
        Returns:
            Dict: 天気予報データ、失敗時はNone
        """
        try:
            url = f"{JMAWeatherAPI.FORECAST_URL}{area_code}.json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"天気予報取得エラー: {e}")
            return None
    
    @staticmethod
    def format_area_data(area_data: Dict) -> List[Dict[str, str]]:
        """
        地域データを整形
        
        Args:
            area_data: 地域データ
            
        Returns
            List[Dict]: セレクトボックス用の地域リスト
        """
        areas = []
        
        if area_data and "centers" in area_data:
            for code, center in area_data["centers"].items():
                areas.append({
                    "code": code,
                    "name": center.get("name", ""),
                })
        
        # 名前でソート
        areas.sort(key=lambda x: x["name"])
        return areas