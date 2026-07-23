x_axis_choice = st.sidebar.selectbox(
        "表示する指標（横軸）を選んでください：",
        axis_options,
        index=4  # デフォルト: 44歳以下の視聴者（リストの5番目）
    )

    y_axis_choice = st.sidebar.selectbox(
        "表示する指標（縦軸）を選んでください：",
        ["再生数", "クリック率", "平均再生率", "44歳以下の視聴者", "登録者数"],
        index=0  # デフォルト: 再生数（リストの1番目）
    )