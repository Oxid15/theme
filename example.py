from theme import Theme


id2label = {
    '0': 'fake',
    '1': 'real'
}

t = Theme(
    id2label=id2label,
    text_col='text',
    show_cols=['title'],
    unmarked_table='data.csv',
    marked_table='markup.csv',
    label_col='label',
    id_col='Unnamed: 0',
    select_label=None,
    write_meta=True,
    assessor_name='Ilia Moiseev',
    meta_prefix={'labeling_goal': 'Generate initial dataset'}
)

t.run()
