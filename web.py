import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
from geopy.distance import geodesic
from datetime import datetime

from kbo_data import KBO_TEAMS
import kbo_service

# 웹 대시보드 기본 페이지 설정
st.set_page_config(
    page_title="KBO 한국프로야구 정보 대시보드",
    page_icon="⚾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS 디자인
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #0F172A;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border-radius: 12px;
        padding: 16px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .team-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.85rem;
    }
    .news-card {
        padding: 12px 16px;
        margin-bottom: 10px;
        background-color: #FFFFFF;
        border-left: 4px solid #3B82F6;
        border-radius: 6px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    .news-card a {
        text-decoration: none;
        color: #1E293B;
        font-weight: 600;
    }
    .news-card a:hover {
        color: #2563EB;
    }
</style>
""", unsafe_allow_html=True)

# 헤더 영역
col_h1, col_h2 = st.columns([4, 1])
with col_h1:
    st.markdown('<div class="main-title">⚾ KBO 한국프로야구 대시보드</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">10개 구단 순위, 경기 일정 및 결과, 개인 성적 랭킹, 전국 홈구장 지도 및 최신 뉴스</div>', unsafe_allow_html=True)
with col_h2:
    if st.button("🔄 실시간 데이터 새로고침", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# 사이드바 설정
st.sidebar.title("⚾ KBO 네비게이션")
menu = st.sidebar.radio(
    "메뉴 이동",
    ["📊 정규리그 순위", "📅 경기 일정 & 결과", "⭐ 개인 성적 랭킹", "🏟️ 전국 홈구장 투어", "📰 최신 KBO 뉴스", "🏟️ 10개 구단 프로필"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.subheader("🌟 선호 구단 선택")
favorite_team = st.sidebar.selectbox("응원하는 팀을 선택하세요", list(KBO_TEAMS.keys()), index=0)
fav_info = KBO_TEAMS[favorite_team]

st.sidebar.markdown(f"""
<div style="background-color: {fav_info['color']}15; border-left: 5px solid {fav_info['color']}; padding: 12px; border-radius: 8px;">
    <div style="display: flex; align-items: center; gap: 10px;">
        <img src="{fav_info['logo_url']}" width="42" height="42" style="object-fit: contain;">
        <div>
            <b style="font-size: 1.1rem; color: #1E293B;">{fav_info['full_name']}</b><br>
            <span style="font-size: 0.85rem; color: #64748B;">연고지: {fav_info['city']} | 우승 {fav_info['championships']}회</span>
        </div>
    </div>
    <div style="font-size: 0.85rem; color: #475569; margin-top: 8px;">
        <b>홈구장:</b> {fav_info['stadium_name']} ({fav_info['stadium_capacity']})
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.caption("데이터 출처: KBO 공식 / 네이버 스포츠 / 구글 뉴스 RSS")


# ==========================================
# 1. 정규리그 순위 탭
# ==========================================
if menu == "📊 정규리그 순위":
    st.subheader("📊 KBO 정규리그 팀 순위표")
    
    df_ranks = kbo_service.get_kbo_rankings()
    
    # 상단 요약 카드 (1위, 2위, 3위)
    top3 = df_ranks.head(3).to_dict('records')
    cols = st.columns(3)
    rank_emojis = ["🥇 1위", "🥈 2위", "🥉 3위"]
    for i, col in enumerate(cols):
        if i < len(top3):
            tname = top3[i]["팀명"]
            tmeta = KBO_TEAMS.get(tname, {})
            with col:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, {tmeta.get('color', '#334155')}18, #F8FAFC); border-radius: 12px; padding: 16px; border: 1px solid #E2E8F0;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 700; color: #475569;">{rank_emojis[i]}</span>
                        <img src="{tmeta.get('logo_url', '')}" width="36" height="36">
                    </div>
                    <h3 style="margin: 8px 0 4px 0; color: #0F172A;">{tmeta.get('full_name', tname)}</h3>
                    <p style="margin: 0; color: #64748B; font-size: 0.95rem;">
                        <b>{top3[i]['승']}승 {top3[i]['무']}무 {top3[i]['패']}패</b> (승률 {top3[i]['승률']:.3f})
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 순위 데이터프레임 스타일링
    st.dataframe(
        df_ranks,
        column_config={
            "순위": st.column_config.NumberColumn("순위", width="small"),
            "팀명": st.column_config.TextColumn("구단명", width="medium"),
            "승률": st.column_config.NumberColumn("승률", format="%.3f"),
            "게임차": st.column_config.TextColumn("게임차"),
        },
        use_container_width=True,
        hide_index=True
    )
    
    # 승률 비교 시각화 차트
    st.subheader("📈 구단별 승률 및 전적 비교")
    fig = px.bar(
        df_ranks,
        x="팀명",
        y="승",
        color="팀명",
        color_discrete_map={k: v["color"] for k, v in KBO_TEAMS.items()},
        text="승",
        title="구단별 정규리그 다승 현황",
        labels={"승": "승리 수", "팀명": "구단"}
    )
    fig.update_layout(showlegend=False, template="plotly_white", height=380)
    st.plotly_chart(fig, use_container_width=True)


# ==========================================
# 2. 경기 일정 & 결과 탭
# ==========================================
elif menu == "📅 경기 일정 & 결과":
    st.subheader("📅 KBO 경기 일정 및 스코어보드")
    
    df_sched = kbo_service.get_kbo_schedule()
    
    if not df_sched.empty:
        # 스코어 카드 뷰
        for _, row in df_sched.iterrows():
            away_team = row.get("원정팀", "-")
            home_team = row.get("홈팀", "-")
            away_color = KBO_TEAMS.get(away_team, {}).get("color", "#64748B")
            home_color = KBO_TEAMS.get(home_team, {}).get("color", "#64748B")
            away_logo = KBO_TEAMS.get(away_team, {}).get("logo_url", "")
            home_logo = KBO_TEAMS.get(home_team, {}).get("logo_url", "")
            
            st.markdown(f"""
            <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 14px 20px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; border-bottom: 1px solid #F1F5F9; padding-bottom: 6px;">
                    <span style="font-weight: 600; color: #3B82F6;">🕒 {row.get('일시')} | 🏟️ {row.get('구장')} 구장</span>
                    <span style="font-size: 0.85rem; color: #64748B; background-color: #F1F5F9; padding: 2px 8px; border-radius: 4px;">중계: {row.get('중계', '-')}</span>
                </div>
                <div style="display: flex; align-items: center; justify-content: space-around; text-align: center;">
                    <div style="flex: 1;">
                        <img src="{away_logo}" width="40" height="40" style="vertical-align: middle;"><br>
                        <b style="font-size: 1.15rem; color: {away_color};">{away_team}</b><br>
                        <small style="color: #64748B;">{row.get('원정투수/비고', '')}</small>
                    </div>
                    <div style="flex: 1; font-size: 1.8rem; font-weight: 800; color: #0F172A;">
                        {row.get('원정점수', '-')} : {row.get('홈팀점수', '-')}
                    </div>
                    <div style="flex: 1;">
                        <img src="{home_logo}" width="40" height="40" style="vertical-align: middle;"><br>
                        <b style="font-size: 1.15rem; color: {home_color};">{home_team}</b><br>
                        <small style="color: #64748B;">{row.get('홈투수/비고', '')}</small>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with st.expander("📋 표 형식으로 자세히 보기"):
            st.dataframe(df_sched, use_container_width=True, hide_index=True)
    else:
        st.info("현재 예정된 경기 일정이 없습니다.")


# ==========================================
# 3. 개인 성적 랭킹 탭
# ==========================================
elif menu == "⭐ 개인 성적 랭킹":
    st.subheader("⭐ KBO 개인 기록 부문별 랭킹")
    
    cat = st.radio("포지션 선택", ["⚾ 타자 부문", "🎯 투수 부문"], horizontal=True)
    
    if cat == "⚾ 타자 부문":
        sub_cat = st.selectbox("부문 선택", list(kbo_service.DEFAULT_BATTERS.keys()))
        data = kbo_service.DEFAULT_BATTERS[sub_cat]
        df_sub = pd.DataFrame(data)
        
        col1, col2 = st.columns([3, 2])
        with col1:
            st.dataframe(df_sub, use_container_width=True, hide_index=True)
        with col2:
            fig = px.bar(
                df_sub,
                x="선수명",
                y=sub_cat,
                color="팀명",
                color_discrete_map={k: v["color"] for k, v in KBO_TEAMS.items()},
                title=f"타자 {sub_cat} TOP 5",
                text=sub_cat
            )
            fig.update_layout(template="plotly_white", height=320)
            st.plotly_chart(fig, use_container_width=True)
            
    else:
        sub_cat = st.selectbox("부문 선택", list(kbo_service.DEFAULT_PITCHERS.keys()))
        data = kbo_service.DEFAULT_PITCHERS[sub_cat]
        df_sub = pd.DataFrame(data)
        
        col1, col2 = st.columns([3, 2])
        with col1:
            st.dataframe(df_sub, use_container_width=True, hide_index=True)
        with col2:
            fig = px.bar(
                df_sub,
                x="선수명",
                y=sub_cat,
                color="팀명",
                color_discrete_map={k: v["color"] for k, v in KBO_TEAMS.items()},
                title=f"투수 {sub_cat} TOP 5",
                text=sub_cat
            )
            fig.update_layout(template="plotly_white", height=320)
            st.plotly_chart(fig, use_container_width=True)


# ==========================================
# 4. 전국 홈구장 투어 탭 (지도 시각화)
# ==========================================
elif menu == "🏟️ 전국 홈구장 투어":
    st.subheader("🏟️ KBO 10개 구단 전국 홈구장 맵")
    st.markdown("지도를 클릭하거나 이동하여 전국의 KBO 야구장 위치와 구장 정보를 확인할 수 있습니다.")
    
    # 대한민국 중심 좌표로 Folium 맵 생성
    m = folium.Map(location=[36.3, 127.8], zoom_start=7, tiles="CartoDB positron")
    
    for team, info in KBO_TEAMS.items():
        popup_html = f"""
        <div style="font-family: sans-serif; width: 220px;">
            <div style="background-color:{info['color']}; color:white; padding: 6px; border-radius: 4px; font-weight: bold; text-align: center;">
                {info['full_name']}
            </div>
            <p style="margin: 6px 0 2px 0;"><b>구장:</b> {info['stadium_name']}</p>
            <p style="margin: 0 0 4px 0;"><b>수용인원:</b> {info['stadium_capacity']}</p>
            <p style="margin: 0 0 6px 0; font-size: 0.85rem; color: #555;">{info['address']}</p>
            <a href="{info['website']}" target="_blank" style="color: #0284c7; text-decoration: none; font-size: 0.85rem;">공식 웹사이트 바로가기 →</a>
        </div>
        """
        
        folium.Marker(
            location=[info["lat"], info["lon"]],
            popup=folium.Popup(popup_html, max_width=260),
            tooltip=f"{info['full_name']} ({info['stadium_name']})",
            icon=folium.Icon(color="red" if team == favorite_team else "blue", icon="info-sign")
        ).add_to(m)
        
    st_folium(m, width="100%", height=500)
    
    # 홈구장 간 직선 거리 계산기
    st.markdown("---")
    st.subheader("📏 구장 간 직선거리 계산기")
    c1, c2 = st.columns(2)
    with c1:
        team_a = st.selectbox("출발 구단/구장", list(KBO_TEAMS.keys()), index=0)
    with c2:
        team_b = st.selectbox("도착 구단/구장", list(KBO_TEAMS.keys()), index=1)
        
    loc_a = (KBO_TEAMS[team_a]["lat"], KBO_TEAMS[team_a]["lon"])
    loc_b = (KBO_TEAMS[team_b]["lat"], KBO_TEAMS[team_b]["lon"])
    dist_km = geodesic(loc_a, loc_b).km
    
    st.success(f"📍 **{KBO_TEAMS[team_a]['stadium_name']}** 부터 **{KBO_TEAMS[team_b]['stadium_name']}** 까지의 직선거리는 약 **{dist_km:.1f} km** 입니다!")


# ==========================================
# 5. 최신 KBO 뉴스 탭
# ==========================================
elif menu == "📰 최신 KBO 뉴스":
    st.subheader("📰 KBO 실시간 야구 뉴스 피드")
    news_list = kbo_service.get_kbo_news()
    
    if news_list:
        for item in news_list:
            st.markdown(f"""
            <div class="news-card">
                <a href="{item['link']}" target="_blank">{item['title']}</a>
                <div style="font-size: 0.85rem; color: #64748B; margin-top: 4px;">
                    <span>📰 {item['source']}</span> &nbsp;•&nbsp; <span>🕒 {item['pubDate']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("뉴스를 불러오는 중입니다.")


# ==========================================
# 6. 10개 구단 프로필 탭
# ==========================================
elif menu == "🏟️ 10개 구단 프로필":
    st.subheader("🏟️ KBO 10개 구단 상세 프로필")
    
    selected = st.selectbox("살펴볼 구단을 선택하세요", list(KBO_TEAMS.keys()))
    info = KBO_TEAMS[selected]
    
    pcol1, pcol2 = st.columns([1, 2])
    with pcol1:
        st.image(info["logo_url"], width=180)
        st.markdown(f"""
        <div style="margin-top: 10px;">
            <a href="{info['website']}" target="_blank" style="display: block; text-align: center; background-color: {info['color']}; color: {info['font_color']}; padding: 10px; border-radius: 8px; text-decoration: none; font-weight: bold;">
                구단 공식 홈페이지 방문 🌐
            </a>
        </div>
        """, unsafe_allow_html=True)
        
    with pcol2:
        st.markdown(f"### {info['full_name']}")
        st.markdown(f"*{info['description']}*")
        
        info_data = {
            "구분": ["연고지", "창단 연도", "한국시리즈 우승", "홈구장", "수용 인원", "구장 주소"],
            "정보": [info["city"], f"{info['founded']}년", f"{info['championships']}회", info["stadium_name"], info["stadium_capacity"], info["address"]]
        }
        st.table(pd.DataFrame(info_data))

st.markdown("---")
st.caption("⚾ 2026 KBO 한국프로야구 정보 대시보드 | Powered by Python & Streamlit")
