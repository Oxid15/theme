import os
import json
from datetime import datetime
from dateutil import tz
from typing import Union, Dict, List, Generator, Any

import pandas as pd
import numpy as np


colors = {
    'K': '\x1B[3om',
    'R': '\x1B[31m',
    'G': '\x1B[32m',
    'Y': '\x1B[33m',
    'B': '\x1B[34m',
    'M': '\x1B[35m',
    'C': '\x1B[36m',
    'W': '\x1B[37m'
}


def cprint(color: str, *args: Any, **kwargs: Any):
    """
    Prints value with given color

    Parameters
    ----------
    color: str
        Any value from [K, R, G, Y, B, M, C, W]
    *args: Any
        regular print arguments
    **kwargs: Any
        regular print arguments
    """
    print(colors[color], end='')
    print(*args, **kwargs)
    print(colors['W'], end='')


class Theme:
    """
    Class that encapsulates labeling process.

    Parameters
    ----------
    id2label: Dict[str, Any]
        The dictionary that maps symbols that user
        inputs to actual values that will be written
        into the final table.

        For example with {'0': 'ham', '1': 'spam'} the user
        will be prompted to type 0 or 1 and the table will receive
        'ham' and 'spam' strings.
    unmarked_table: str
        Path to the .csv file where the texts are stored
    marked_table: str
        Path to the .csv file where marked texts will be stored. Creates new
        if does not exist.
    id_col: str
        The column with which texts can be identified
    text_col: str
        The name of the column where the text that will be labeled is stored
    label_col: str
        The column name where labels should be written
    show_cols: Union[List[str], None], optional
        Additional columns that should be presented when labeling. For example `title`
    show_chars: int, default 500
        How many characters of the text to show from the first one
    select_label: Union[str, None], optional
        If data is prelabeled can select some values using `label_col`
    skip_input: str, default " "
        The character that user should write to skip the text
    back_input: str, default "b"
        The character that user should write to edit previous label
    more_input: str, default ""
        The character that user should write to print more text,
        prints `show_chars` characters until the end of text
    write_meta: bool, optional
        Whether to write JSON metadata file
    meta_prefix: dict, optional
        The dictionary that will be used to update() meta before saving.
        Pass here any additional values that need to be included in metadata.
        Will be ignored if write_meta == False
    cache_skipped: bool, optional
        Whether to write cached text's ids to disk to reuse them between sessions.
    cache_folder: str, optional
        Where to save cache.json file with ids of skipped texts. Used only if
        cache_skipped == True. Default is ./.theme
    """
    def __init__(
        self,
        id2label: Dict[str, Any],
        unmarked_table: str,
        marked_table: str,
        id_col: str,
        text_col: str,
        label_col: str,
        show_cols: Union[List[str], None] = None,
        show_chars: int = 500,
        select_label: Union[str, None] = None,
        skip_input: str = ' ',
        back_input: str = 'b',
        more_input: str = '',
        write_meta: bool = False,
        meta_prefix: Union[Dict[Any, Any], None] = None,
        cache_skipped: bool = False,
        cache_folder: str = '.theme'
    ) -> None:
        self._id2label = id2label
        self._text_col = text_col
        self._unmarked_table = unmarked_table
        self._marked_table = marked_table
        self._label_col = label_col
        self._id_col = id_col
        self._show_chars = show_chars
        self._select_label = select_label
        self._to_write_meta = write_meta
        self._cache_skipped = cache_skipped
        self._cache_folder = cache_folder
        if meta_prefix is not None:
            self._meta_prefix = meta_prefix
        else:
            self._meta_prefix = {}

        self._input_map = {
            skip_input: 'skip',
            back_input: 'back',
            more_input: 'more'
        }

        if show_cols is None:
            self._show_cols = []
        else:
            self._show_cols = show_cols

        self._initialize_cache()

        self._marked_history = []
        self._unmarked = pd.DataFrame()
        self._marked = pd.DataFrame()
        self._chars_showed = 0

        self._load_data()

        self._unmarked_indices = [i for i in range(len(self._unmarked))]
        np.random.shuffle(self._unmarked_indices)

        self._marked_indices = []

        self._check_values()

    def _check_values(self) -> None:
        for inp in self._id2label:
            if inp in self._input_map:
                raise ValueError(
                    f'\'{inp}\' string from id2label already present in commands. '
                    f'Either change the \'{self._input_map[inp]}\' command or a value in id2label'
                )

        missing_cols = []
        for col in self._show_cols + [self._text_col, self._id_col]:
            if col not in self._unmarked:
                missing_cols.append(col)

        if len(missing_cols):
            raise ValueError(
                f'{missing_cols} from id2label not in the table columns: {list(self._unmarked.columns)}')

        for inp in self._id2label:
            if not isinstance(inp, str):
                raise ValueError(
                    f'{inp} in id2label is not string. Please, pass values that the user will type as strings'
                )

    def _load_data(self) -> None:
        self._unmarked = pd.read_csv(self._unmarked_table)
        if self._label_col in self._unmarked and self._select_label is not None:
            self._unmarked = self._unmarked[self._unmarked[self._label_col] == self._select_label]
        else:
            self._unmarked[self._label_col] = None

        if os.path.exists(self._marked_table):
            self._marked = pd.read_csv(self._marked_table)
        else:
            self._marked = pd.DataFrame(columns=self._unmarked.columns)

    def _initialize_cache(self) -> None:
        unmarked_filename = os.path.split(self._unmarked_table)[-1]

        self._cache = {unmarked_filename: {'skipped': []}}

        if self._cache_skipped:
            cache_path = os.path.join(self._cache_folder, 'cache.json')
            if os.path.exists(cache_path):
                with open(cache_path, 'r') as f:
                    self._cache = json.load(f)

        if unmarked_filename not in self._cache:
            self._cache[unmarked_filename] = {'skipped': []}

        if 'skipped' not in self._cache[unmarked_filename]:
            self._cache[unmarked_filename]['skipped'] = []

        self._skipped = self._cache[unmarked_filename]['skipped']

    def _was_marked(self, i) -> bool:
        if self._unmarked[self._id_col][i] in self._marked[self._id_col]:
            return True
        else:
            return False

    def _was_skipped(self, i) -> bool:
        if i in self._skipped:
            return True
        else:
            return False

    def _show_options(self) -> None:
        cprint('G', self._input_map)
        cprint('G', self._id2label)

    def _show_menu(self, row) -> None:
        print('')
        cprint('G', f'Marked: {len(self._marked)}')
        cprint('G', f'Unmarked: {len(self._unmarked)}')
        cprint('G', f'Skipped: {len(self._skipped)}')
        self._show_options()
        print('')
        if self._show_cols is not None:
            for i, col in enumerate(self._show_cols):
                if pd.notna(row[col]):
                    print(f'{col}: {row[col]}')
                else:
                    cprint('R', f'{col}: NaN')
        print('')

        if pd.notna(row[self._text_col]):
            print(row[self._text_col][:self._show_chars])
            self._chars_showed += min(len(row[self._text_col]), self._show_chars)
        else:
            cprint('R', 'EMPTY TEXT')

    def _get_user_input(self) -> str:
        while True:
            label = input()
            if label in self._input_map:
                label = self._input_map[label]
                break
            elif label in self._id2label:
                break
            else:
                self._show_options()
        return label

    def _sample_generator(self) -> Generator:
        while True:
            if len(self._unmarked_indices) > 0:
                yield self._unmarked_indices[0]
            else:
                break

    def _write(self) -> None:
        self._marked.to_csv(self._marked_table, index=False)

    def _skip(self) -> None:
        index = self._unmarked_indices.pop(0)
        self._skipped.append(index)
        self._chars_showed = 0

        if self._cache_skipped:
            with open(os.path.join(self._cache_folder, 'cache.json'), 'w') as f:
                json.dump(self._cache, f)

        cprint('R', 'SKIPPED')

    def _back(self) -> None:
        if len(self._marked_indices) > 0:
            index = self._marked_indices.pop(-1)
            self._unmarked_indices.insert(0, index)
            self._marked = self._marked[:-1]
            self._chars_showed = 0
            cprint('R', 'BACK')
        else:
            cprint('R', 'HISTORY IS EMPTY')

    def _more(self, row) -> None:
        if pd.notna(row[self._text_col]):
            text = row[self._text_col]
            start = self._chars_showed
            end = min(start + self._show_chars, len(text))

            if start == len(text):
                cprint('R', 'END')
            elif end <= len(text):
                print(text[start:end])
                self._chars_showed = end
        else:
            cprint('R', 'CAN\'T SHOW MORE')

    def _write_meta(self):
        meta = {
            'saved_at': str(datetime.now(tz=tz.gettz('UTC'))),
            'size': len(self._marked)
        }
        meta.update(self._meta_prefix)
        try:
            with open(os.path.join(os.path.dirname(self._marked_table), 'meta.json'), 'w') as f:
                json.dump(meta, f)
        except Exception as e:
            raise RuntimeError('Error while writing metadata') from e

    def run(self) -> None:
        """
        Method that runs the labeling process.

        Samples are selected randomly.

        The info on number of already marked, unmarked and skipped presented to the
        user first. Then the available options are printed - what input for what class.

        Finally there are some additional user-defined fields and the text to label itself.
        The user is prompted to choose the label.

        If the label is not in the `id2label`  the user is prompted to enter the label again.
        User can skip, edit previous label or request more characters from text using commands
        that are determined by the `__init__` parameters.

        The whole marked table is saved to the disk at each iteration.
        """
        if self._cache_skipped:
            os.makedirs(self._cache_folder, exist_ok=True)

        label = None
        for i in self._sample_generator():
            if self._was_marked(i):
                self._unmarked_indices.pop(0)
                continue

            if self._was_skipped(i):
                self._unmarked_indices.pop(0)
                continue

            row = self._unmarked.iloc[i].copy(deep=True)

            # If label got in previous cycle is more
            # don't show initial parts of the text
            if label != 'more':
                self._show_menu(row)
            label = self._get_user_input()

            if label == 'skip':
                self._skip()
                continue
            elif label == 'back':
                self._back()
                continue
            elif label == 'more':
                self._more(row)
            else:
                row[self._label_col] = self._id2label[label]
                self._marked = pd.concat((self._marked, pd.DataFrame([row])))
                self._write()
                if self._to_write_meta:
                    self._write_meta()

                index = self._unmarked_indices.pop(0)
                self._marked_indices.append(index)

        print('All marked')
