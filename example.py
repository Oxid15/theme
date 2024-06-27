from theme import Theme

id2label = {"0": "fake", "1": "real"}

t = Theme(
    id2label=id2label,
    unmarked_table="data.csv",
    marked_table="markup.csv",
    id_col="id",
    text_col="text",
    label_col="label",
    show_cols=["title"],
    select_label=None,
    write_meta=True,
    meta_prefix={"labeling_goal": "Generate initial dataset"},
    cache_skipped=True,
    show_chars=100,
    label_session_minutes=2,
    break_minutes=1,
)

t.run()
