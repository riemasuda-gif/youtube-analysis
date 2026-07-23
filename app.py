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

    # 2. サイドバーで横軸・縦軸を自由に選択可能に変更
    axis_options = ["投稿日", "再生数", "クリック率", "平均再生率", "44歳以下の視聴者", "登録者数"]

    x_axis_choice = st.sidebar.selectbox(
        "表示する指標（横軸）を選んでください：",
        axis_options,
        index=0  # デフォルト: 投稿日
    )

    y_axis_choice = st.sidebar.selectbox(
        "表示する指標（縦軸）を選んでください：",
        ["再生数", "クリック率", "平均再生率", "44歳以下の視聴者", "登録者数"],
        index=3  # デフォルト: 44歳以下の視聴者
    )

    # 横軸のデータ型判定（投稿日の場合は名目:N、数値データの場合は数量:Q）
    x_type = ":N" if x_axis_choice == "投稿日" else ":Q"
    x_sort = "ascending" if x_axis_choice == "投稿日" else None

    # 3. ホバー判定およびXY軸ズーム設定
    hover = alt.selection_point(
        on="pointerover", clear="pointerout", empty=False
    )
    zoom_axes = alt.selection_interval(bind="scales", encodings=["x", "y"])

    # 4. 共通の軸・データエンコーディング
    base = alt.Chart(df).encode(
        x=alt.X(
            f"{x_axis_choice}{x_type}",
            title=x_axis_choice,
            sort=x_sort
        ),
        y=alt.Y(
            f"{y_axis_choice}:Q",
            title=y_axis_choice,
            scale=alt.Scale(domainMin=-10),
        ),
        url="サムネイルURL:N",
        tooltip=["投稿日:N", "再生数:Q", "クリック率:Q", "平均再生率:Q", "44歳以下の視聴者:Q", "登録者数:Q"],
    )

    # 通常表示層（標準サイズ：幅80×高さ50）
    chart_base = base.mark_image(width=80, height=50)

    # ホバー判定専用層（透明な判定領域：幅80×高さ50）
    chart_event = base.mark_image(width=80, height=50, opacity=0).add_params(
        hover
    )

    # ホバー時拡大表示層（200%拡大：幅160×高さ100）
    chart_hover = base.mark_image(width=160, height=100).transform_filter(
        hover
    )

    # 5. 重ね合わせ・動的タイトルの追加（高さ950px）
    chart = (
        alt.layer(chart_base, chart_hover, chart_event)
        .add_params(zoom_axes)
        .properties(
            height=950,
            title=f"■ {x_axis_choice}（横） × {y_axis_choice}（縦）の分析グラフ",
        )
    )

    # 画面幅いっぱいに固定表示
    st.altair_chart(chart, use_container_width=True)

except FileNotFoundError:
    st.error(
        "youtube_data.csv が見つかりません。app.pyと同じフォルダに置いてください。"
    )
except Exception as e:
    st.error("予期せぬエラーが発生しました：")
    st.exception(e)