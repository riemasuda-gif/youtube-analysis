import altair as alt
import pandas as pd
import streamlit as st

# 1. 画面の表示幅をワイドモードに設定
st.set_page_config(layout="wide")

st.subheader("ノーブルホームサムネ分析")

try:
    df = pd.read_csv("youtube_data.csv", encoding="utf-8-sig")
    df.columns = df.columns.str.strip()

    # 数値列のカンマや%を除去して数値型に変換
    # 対象カラムに「44歳以下の視聴者」「登録者数」を追加
    num_cols = ["再生数", "クリック率", "平均再生率", "44歳以下の視聴者", "登録者数"]
    for col in num_cols:
        if col in df.columns and df[col].dtype == "object":
            df[col] = (
                df[col]
                .astype(str)
                .str.replace("%", "")
                .str.replace(",", "")
                .str.replace("-", "")  # ハイフンを除去
            )
            # errors="coerce"により、数値化できない値は自動でNaNになりエラーを回避
            df[col] = pd.to_numeric(df[col], errors="coerce")

    expected_cols = [
        "投稿日",
        "サムネイルURL",
        "再生数",
        "クリック率",
        "平均再生率",
        "44歳以下の視聴者",
        "登録者数"
    ]
    missing_cols = [c for c in expected_cols if c not in df.columns]

    if missing_cols:
        st.error(f"CSVの中に以下の列が見つかりません: {missing_cols}")
        st.info(f"現在認識されている列名: {list(df.columns)}")
        st.stop()

    # 2. 選択項目をサイドバーに移動して固定
    y_axis_choice = st.sidebar.selectbox(
        "表示する指標（縦軸）を選んでください：",
        ["再生数", "クリック率", "平均再生率", "44歳以下の視聴者", "登録者数"],
    )

    # 3. ホバー判定およびズーム設定
    hover = alt.selection_point(
        on="pointerover", clear="pointerout", empty=False
    )
    zoom_y = alt.selection_interval(bind="scales", encodings=["y"])
    zoom_xy = alt.selection_interval(bind="scales", encodings=["x", "y"])  # 追加グラフ用（XY両軸ズーム）

    # ====================================================================
    # 既存のグラフ（横軸：投稿日 固定）
    # ====================================================================
    base = alt.Chart(df).encode(
        x=alt.X("投稿日:N", title="投稿日", sort="ascending"),
        y=alt.Y(
            f"{y_axis_choice}:Q",
            title=y_axis_choice,
            scale=alt.Scale(domainMin=-10),
        ),
        url="サムネイルURL:N",
        tooltip=["投稿日:N", "再生数:Q", "クリック率:Q", "平均再生率:Q", "44歳以下の視聴者:Q", "登録者数:Q"],
    )

    chart_base = base.mark_image(width=80, height=50)
    chart_event = base.mark_image(width=80, height=50, opacity=0).add_params(hover)
    chart_hover = base.mark_image(width=160, height=100).transform_filter(hover)

    chart = (
        alt.layer(chart_base, chart_hover, chart_event)
        .add_params(zoom_y)
        .properties(
            height=950,
            title=f"■ {y_axis_choice}の推移",
        )
    )

    st.altair_chart(chart, use_container_width=True)

    # ====================================================================
    # 追加のグラフ（横軸：44歳以下の視聴者 × 縦軸：再生数 固定）
    # ====================================================================
    st.markdown("---")  # 区切り線
    st.subheader("追加分析")

    base_add = alt.Chart(df).encode(
        x=alt.X("44歳以下の視聴者:Q", title="44歳以下の視聴者"),
        y=alt.Y("再生数:Q", title="再生数", scale=alt.Scale(domainMin=-10)),
        url="サムネイルURL:N",
        tooltip=["投稿日:N", "再生数:Q", "クリック率:Q", "平均再生率:Q", "44歳以下の視聴者:Q", "登録者数:Q"],
    )

    chart_add_base = base_add.mark_image(width=80, height=50)
    chart_add_event = base_add.mark_image(width=80, height=50, opacity=0).add_params(hover)
    chart_add_hover = base_add.mark_image(width=160, height=100).transform_filter(hover)

    chart_add = (
        alt.layer(chart_add_base, chart_add_hover, chart_add_event)
        .add_params(zoom_xy)
        .properties(
            height=950,
            title="■ 44歳以下の視聴者（横） × 再生数（縦）"
        )
    )

    st.altair_chart(chart_add, use_container_width=True)

except FileNotFoundError:
    st.error(
        "youtube_data.csv"
        " が見つかりません。app.pyと同じフォルダに置いてください。"
    )
except Exception as e:
    st.error("予期せぬエラーが発生しました：")
    st.exception(e)