from theme import Theme


id2label = {
    '0': 'ham',
    '1': 'spam'
}

Theme(
    id2label=id2label,
    text_col='main_text',
    show_cols=['title'],
    unmarked_table='./data.csv',
    marked_table='./markup.csv',
    label_col='label',
    id_col='id',
    select_label=None
).run()
