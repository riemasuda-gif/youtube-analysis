import altair as alt
import pandas as pd
import streamlit as st

# 1. 画面の表示幅をワイドモードに設定
st.set_page_config(layout="wide")

st.title("YouTube動画分析ダッシュボード")

try:
    df = pd.read_csv("youtube_data.csv", encoding="utf-8-sig")
    df.columns = df.columns.str.strip()

    # 数値列のカンマや%を除去して数値型に変換
    num_cols = ["再生数", "クリック率", "平均再生率"]
    for col in num_cols:
        if col in df.columns and df[col].dtype == "object":
            df[col] = (
                df[col]
                .astype(str)
                .str.replace("%", "")
                .str.replace(",", "")
            )
            df[col] = pd.to_numeric(df[col], errors="coerce")

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

    # 2. 選択項目をサイドバーに移動して固定
    y_axis_choice = st.sidebar.selectbox(
        "表示する指標（縦軸）を選んでください：",
        ["再生数", "クリック率", "平均再生率"],
    )

    # 3. ホバー判定およびY軸ズーム設定
    hover = alt.selection_point(on="pointerover", clear="pointerout")
    zoom_y = alt.selection_interval(bind="scales", encodings=["y"])

    # 4. 共通の軸・データエンコーディング
    base = alt.Chart(df).encode(
        x=alt.X("投稿日:N", title="投稿日", sort="ascending"),
        y=alt.Y(
            f"{y_axis_choice}:Q",
            title=y_axis_choice,
            scale=alt.Scale(domainMin=-100),
        ),
        url="サムネイルURL:N",
    )

    # 通常表示層（幅80×高さ50）
    chart_base = base.mark_image(width=80, height=50)

    # ホバー判定専用層（透明な判定領域を固定配置し、判定ブレやチラつきを防止）
    chart_event = base.mark_image(width=80, height=50, opacity=0).add_params(hover)

    # ホバー時拡大表示層（200%拡大：幅160×高さ100 ＋ ツールチップ表示）
    chart_hover = (
        base.mark_image(width=160, height=100)
        .encode(
            tooltip=["投稿日:N", "再生数:Q", "クリック率:Q", "平均再生率:Q"]
        )
        .transform_filter(hover)
    )

    # 5. 重ね合わせ・動的タイトルの追加
    chart = (
        alt.layer(chart_base, chart_hover, chart_event)
        .add_params(zoom_y)
        .properties(
            height=500,
            title=f"■ {y_axis_choice}の推移",
        )
    )

    # 画面幅いっぱいに固定表示
    st.altair_chart(chart, use_container_width=True)

except FileNotFoundError:
    st.error(
        "youtube_data.csv"
        " が見つかりません。app.pyと同じフォルダに置いてください。"
    )
except Exception as e:
    st.error("予期せぬエラーが発生しました：")
    st.exception(e)