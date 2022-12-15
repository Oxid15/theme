import os
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
    text_col: str
        The name of the column where the text that will be labeled is stored
    unmarked_table: str
        Path to the .csv file where the texts are stored
    marked_table: str
        Path to the .csv file where marked texts will be stored. Creates new
        if does not exist.
    label_col: str
        The column name where labels should be written
    id_col: str
        The column with which texts can be identified
    show_cols: Union[List[str], None], optional
        Additional columns that should be presented when labeling. For example `title`.
    show_chars: int, default 500
        How many characters of the text to show from the first one
    select_label: Union[str, None], optional
        If data is prelabeled can select some values using `label_col`.
    """
    def __init__(
        self,
        id2label: Dict[str, Any],
        text_col: str,
        unmarked_table: str,
        marked_table: str,
        label_col: str,
        id_col: str,
        show_cols: Union[List[str], None] = None,
        show_chars: int = 500,
        select_label: Union[str, None] = None
    ) -> None:
        self._id2label = id2label
        self._text_col = text_col
        self._unmarked_table = unmarked_table
        self._marked_table = marked_table
        self._label_col = label_col
        self._id_col = id_col
        self._show_chars = show_chars
        self._select_label = select_label
        if show_cols is None:
            self._show_cols = []
        else:
            self._show_cols = show_cols

        self._skipped = set()
        self._marked_history = []
        self._unmarked = pd.DataFrame()
        self._marked = pd.DataFrame()

        self._load_data()

        self._unmarked_indices = [i for i in range(len(self._unmarked))]
        np.random.shuffle(self._unmarked_indices)

        self._marked_indices = []

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
        cprint('G', 'Enter to skip, Space and Enter to edit previous markup')
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
                print(f'{col}: {row[col]}')
        print('')
        print(row[self._text_col][:self._show_chars])

    def _get_user_input(self) -> str:
        while True:
            label = input()
            if label == '':
                label = 'skip'
                break
            elif label == ' ':
                label = 'back'
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

    def _write(self) -> None:
        self._marked.to_csv(self._marked_table, index=False)

    def _skip(self) -> None:
        index = self._unmarked_indices.pop(0)
        self._skipped.add(index)
        cprint('R', 'SKIPPED')

    def _back(self) -> None:
        if len(self._marked_indices) > 0:
            index = self._marked_indices.pop(-1)
            self._unmarked_indices.insert(0, index)
            self._marked = self._marked[:-1]
            cprint('R', 'BACK')
        else:
            cprint('R', 'HISTORY IS EMPTY')

    def run(self) -> None:
        """
        Method that runs the labeling process.

        Samples are selected randomly.

        The info on number of already marked, unmarked and skipped presented to the
        user first. Then the available options are printed - what input for what class.

        Finally there are some additional user-defined fields and the text to label itself.
        The user is prompted to choose the label.

        If entered label is empty, then the text is marked as skipped and will not appear in this
        session.
        If entered label is space, then the previous markedtext is prompted
        instread of current one.
        If the label is not in the `id2label`  the user is prompted to enter the label again.

        The whole marked table is saved to the disk at each iteration.
        """
        for i in self._sample_generator():
            if self._was_marked(i):
                continue

            if self._was_skipped(i):
                continue

            row = self._unmarked.iloc[i].copy(deep=True)
            self._show_menu(row)
            label = self._get_user_input()

            if label == 'skip':
                self._skip()
                continue
            elif label == 'back':
                self._back()
                continue
            else:
                row[self._label_col] = self._id2label[label]
                self._marked = pd.concat((self._marked, pd.DataFrame([row])))
                self._write()

                index = self._unmarked_indices.pop(0)
                self._marked_indices.append(index)

        print('All marked')
