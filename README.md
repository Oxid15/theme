# theme
![ver](https://img.shields.io/github/v/release/oxid15/theme?style=plastic) [![DOI](https://zenodo.org/badge/578688999.svg)](https://zenodo.org/doi/10.5281/zenodo.12591749)  
    
Minimalistic CLI labeling tool for text classification

It allows for the rapid acquisition of manually labeled texts without the need to set up any large-scale labeling solution.

With the fewest requirements possible, one can get an initial dataset to train a text classification model.

## Installation
```bash
pip install theme-label
```

## Usage
To use `Theme` you will need:
- Path to `.csv` or `pandas.DataFrame` with at least *two* columns: the one with texts and their id's
- The following script

```python
from theme import Theme

# This is the dict that maps
# what user enters to what goes
# to the table
id2label = {
    '0': 'ham',
    '1': 'spam'
}

# Here markup session is initialized
# data is loaded and everything prepared
t = Theme(
    id2label=id2label,
    text_col='text', # Name of the column with texts
    show_cols=['title'], # Additional fields to show during labeling
    unmarked_table='data.csv', # Our input table, can be pandas DataFrame
    marked_table='markup.csv', # Output table will have same columns with additional one for label
    label_col='label', # The name of additional column
    id_col='id', # The name of id column
)

# Here is how to start labeling session
t.run()
```

## Labeling process
![](imgs/screen_demo.png)

The info on number of already marked, unmarked and skipped presented to the user first. Then the available options are printed - which input stands for which class.

Finally there are some additional user-defined fields and the text to label. The user is prompted to choose the label.

If entered label is *space*, then the text is marked as skipped and will not appear in this session.  
If entered label is *b*, then previous marked text is prompted instead of current one.  
If entered label is *empty* the user is provided with another portion of the same text.
If the label is not in the `id2label` the user is prompted to enter the label again.

Commands can be reassigned using parameters, see [docstring in the file](theme/theme.py).


## Advanced usage
See [theme/theme.py](theme/theme.py) for documentation.

## Contributing

All contributions are welcome!  
If you have any questions or feature requests feel free to open issues or submit PR's.  

When adding functionality keep in mind that `Theme` is a minimalistic tool that should be kept simple
and not too loaded with dependencies.

## License
[MIT License](LICENSE)

## Versions
This project uses Semantic Versioning - https://semver.org/

## Cite
If you used `Theme` for your project, please cite with:
```bibtex
@software{ilia_moiseev_2024_12591750,
  author       = {Ilia Moiseev},
  title        = {Theme: Minimalistic CLI labeling tool for text classification},
  month        = jun,
  year         = 2024,
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.12591750},
  url          = {https://doi.org/10.5281/zenodo.12591750}
}
```


## Changelog

Here is the history of changes in `Theme`

### v0.3.0
- Session time tracking
- Go back to skipped texts too
- Removes `numpy` from direct dependencies
- Clean exit on `Ctrl+C`
- Select session cache before the start
- More fields in metadata

### v0.2.1
- Fixed missing last characters
- Informative error message
- Check if ids in id2label are strings

### v0.2.0

- Command that allows getting another page of text
- Command keys are now customizable
- Skipped ids are cached on disk
- Write metadata about labeling
- Bugs fixed

### v0.1.0

- First release of `Theme`
- Fixed size of text
- Simple labeling loop
- Mark, skip or go back while labeling
