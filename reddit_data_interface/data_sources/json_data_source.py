import json
from collections import defaultdict
from typing import Collection, Iterable

from reddit_data_interface.data_models import RedditComment
from reddit_data_interface.data_sources.data_source import DataSource


class JsonDataSource(DataSource):
    """
    Load an entire file of Reddit comments into memory and creates indexes with dicts.
    """

    def __init__(self, data_files: Iterable[str]):
        self.comments_by_id = {}
        self.comments_by_parent_id = defaultdict(set)
        for data_file in data_files:
            self._load_data(data_file)

    def _load_data(self, data_file: str):
        with open(data_file, 'r') as f:
            for line in f:
                rc = RedditComment.from_dict(json.loads(line))
                self.comments_by_id[rc.id] = rc
                self.comments_by_parent_id[rc.parent_id].add(rc)

    def get_comment(self, comment_id: str) -> RedditComment:
        return self.comments_by_id.get(comment_id, None)

    def get_children(self, parent_id: str) -> Collection[RedditComment]:
        return self.comments_by_parent_id.get(parent_id, set())

    def iter_parents(self) -> Iterable[RedditComment]:
        for key in self.comments_by_parent_id.keys():
            comment = self.comments_by_id.get(key)
            if comment:
                yield comment

    def iter_roots(self) -> Iterable[RedditComment]:
        for comment in self.comments_by_id.values():
            if comment.is_root():
                yield comment

