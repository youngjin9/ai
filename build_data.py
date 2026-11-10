"""
KBO 최신 데이터 수집 및 data.json 자동 생성 스크립트
GitHub Actions 또는 로컬에서 실행되어 data.json을 최신 상태로 갱신합니다.
"""

import json
import kbo_service
import kbo_data

def build_data():
    print("Collecting KBO rankings...")
    ranks = kbo_service.get_kbo_rankings().to_dict('records')
    
    print("Collecting KBO schedules...")
    sched = kbo_service.get_kbo_schedule().to_dict('records')
    
    print("Collecting KBO news...")
    news = kbo_service.get_kbo_news()
    
    data = {
        'teams': kbo_data.KBO_TEAMS,
        'ranks': ranks,
        'sched': sched,
        'news': news,
        'batters': kbo_service.DEFAULT_BATTERS,
        'pitchers': kbo_service.DEFAULT_PITCHERS
    }
    
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Successfully generated data.json!")

if __name__ == '__main__':
    build_data()
