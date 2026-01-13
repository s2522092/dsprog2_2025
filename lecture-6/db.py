import sqlite3
import os
from datetime import datetime

class WeatherDatabase:
    def __init__(self, db_path="database/weather.db"):
        # パスが相対パスなら、現在のスクリプトからの相対パスに変換
        if not os.path.isabs(db_path):
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), db_path)
            
        # データベースディレクトリが存在しなければ作成
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
        self.db_path = db_path
        self.create_tables()
        
    def get_connection(self):
        """データベース接続を取得"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 結果を辞書形式で取得
        return conn
        
    def create_tables(self):
        """テーブルを作成"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # エリアテーブル
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS areas (
            area_id TEXT PRIMARY KEY,
            area_name TEXT NOT NULL,
            region TEXT NOT NULL,
            display_order INTEGER DEFAULT 0
        )
        ''')
        
        # 天気予報テーブル
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather_forecasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            area_id TEXT NOT NULL,
            forecast_date TEXT NOT NULL,
            weather_code TEXT NOT NULL,
            weather_text TEXT NOT NULL,
            temperature_min REAL,
            temperature_max REAL,
            rainfall_probability INTEGER,
            fetch_timestamp TEXT NOT NULL,
            FOREIGN KEY (area_id) REFERENCES areas(area_id),
            UNIQUE (area_id, forecast_date, fetch_timestamp)
        )
        ''')
        
        conn.commit()
        conn.close()
        
    def insert_area(self, area_id, area_name, region, display_order=0):
        """エリア情報をデータベースに挿入"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT OR REPLACE INTO areas (area_id, area_name, region, display_order)
        VALUES (?, ?, ?, ?)
        ''', (area_id, area_name, region, display_order))
        
        conn.commit()
        conn.close()
        
    def insert_forecast(self, area_id, forecast_date, weather_code, weather_text, 
                        temperature_min, temperature_max, rainfall_probability):
        """天気予報データをデータベースに挿入"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
        INSERT INTO weather_forecasts 
        (area_id, forecast_date, weather_code, weather_text, temperature_min, 
         temperature_max, rainfall_probability, fetch_timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (area_id, forecast_date, weather_code, weather_text, temperature_min, 
              temperature_max, rainfall_probability, current_time))
        
        conn.commit()
        conn.close()
        
    def get_all_areas(self):
        """すべてのエリア情報を取得"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM areas ORDER BY region, display_order, area_name
        ''')
        
        areas = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return areas
    
    def get_forecast(self, area_id, date=None):
        """特定エリアの最新予報データを取得"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if date:
            # 特定日付の予報を取得
            cursor.execute('''
            SELECT * FROM weather_forecasts
            WHERE area_id = ? AND forecast_date = ?
            ORDER BY fetch_timestamp DESC
            LIMIT 1
            ''', (area_id, date))
        else:
            # 最新の予報を全日分取得
            cursor.execute('''
            SELECT f1.* FROM weather_forecasts f1
            JOIN (
                SELECT area_id, forecast_date, MAX(fetch_timestamp) as max_timestamp
                FROM weather_forecasts
                WHERE area_id = ?
                GROUP BY forecast_date
            ) f2
            ON f1.area_id = f2.area_id AND f1.forecast_date = f2.forecast_date 
            AND f1.fetch_timestamp = f2.max_timestamp
            ORDER BY f1.forecast_date
            ''', (area_id,))
        
        forecasts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return forecasts