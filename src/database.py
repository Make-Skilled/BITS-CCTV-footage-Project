import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self):
        # Get the directory where this file is located
        db_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(db_dir, 'video_analysis.db')
        self.init_db()

    def init_db(self):
        """Initialize the database and create tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create table for video analysis results
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS video_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                video_type TEXT NOT NULL,
                video_path TEXT NOT NULL,
                max_count INTEGER NOT NULL,
                total_count INTEGER NOT NULL,
                cumulative_counts TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()

    def save_analysis(self, video_type, video_path, max_count, total_count, cumulative_counts):
        """Save video analysis results to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Convert cumulative_counts list to string for storage
        cumulative_counts_str = ','.join(map(str, cumulative_counts))
        
        cursor.execute('''
            INSERT INTO video_analysis 
            (video_type, video_path, max_count, total_count, cumulative_counts)
            VALUES (?, ?, ?, ?, ?)
        ''', (video_type, video_path, max_count, total_count, cumulative_counts_str))
        
        conn.commit()
        conn.close()

    def get_all_analysis(self):
        """Retrieve all video analysis results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM video_analysis ORDER BY timestamp DESC')
        results = cursor.fetchall()
        
        # Convert results to list of dictionaries
        formatted_results = []
        for row in results:
            formatted_results.append({
                'id': row[0],
                'timestamp': row[1],
                'video_type': row[2],
                'video_path': row[3],
                'max_count': row[4],
                'total_count': row[5],
                'cumulative_counts': [int(x) for x in row[6].split(',')]
            })
        
        conn.close()
        return formatted_results 