import altair as alt
import pandas as pd
import streamlit as st

# 1. 画面の表示幅をワイドモードに設定（画面幅の約90%を活用）
st.set_page_config(layout="wide")

st.title("YouTube動画分析ダッシュボード")

try:
    df = pd.read_csv("youtube_data.csv", encoding="utf-8-sig")
    df.columns = df.columns.str.strip()

    expected_cols = [
        "投稿日",
        "サムネイルURL",
        "再生数",
        "クリック率",
        "平均再生率",
    ]
    missing_cols = [c for c in expected_cols if c not in df.columns]

    if missing_cols:
        st.error(f"CSVの中に以下の列が見つかりません: {missing_cols}")
        st.info(f"現在認識されている列名: {list(df.columns)}")
        st.stop()

    y_axis_choice = st.selectbox(
        "表示する指標（縦軸）を選んでください：",
        ["再生数", "クリック率", "平均再生率"],
    )

    # 2. マウスホバー用のセレクションを定義
    hover = alt.selection_point(on="pointerover", empty=False)

    # 3. 共通の軸・データエンコーディング
    base = alt.Chart(df).encode(
        x=alt.X("投稿日:N", title="投稿日", sort="ascending"),
        y=alt.Y(f"{y_axis_choice}:Q", title=y_axis_choice),
        url="サムネイルURL",
        tooltip=["投稿日", "再生数", "クリック率", "平均再生率"],
    )

    # 通常時の表示（幅80、高さ50）
    chart_base = base.mark_image(width=80, height=50)

    # ホバー時の表示（120%拡大：幅96、高さ60）＋対象データのみフィルター
    chart_hover = base.mark_image(width=96, height=60).transform_filter(
        hover
    )

    # 重ね合わせ（後に指定した chart_hover が最前面に描写されます）
    chart = (
        alt.layer(chart_base, chart_hover)
        .add_params(hover)
        .properties(height=500)
        .interactive()
    )

    st.altair_chart(chart, use_container_width=True)

except FileNotFoundError:
    st.error(
        "youtube_data.csv"
        " が見つかりません。app.pyと同じフォルダに置いてください。"
    )
except Exception as e:
    st.error(f"予期せぬエラーが発生しました: {e}")