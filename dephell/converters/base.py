# built-in
from os import unlink
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Optional, Tuple

# app
from ..constants import FILES
from ..controllers import Graph, Mutator, Resolver
from ..models import RootDependency


class BaseConverter:
    lock = False

    # inspection

    def can_parse(self, path: Path, content: Optional[str] = None) -> bool:
        return False

    # root dependency load and dump

    def loads(self, content: str) -> RootDependency:
        stream = NamedTemporaryFile(mode='w', delete=False)
        stream.write(content)
        stream.close()
        root = self.load(stream.name)
        unlink(stream.name)
        return root

    def load(self, path) -> RootDependency:
        path = Path(str(path))
        with path.open('r', encoding='utf8') as stream:
            return self.loads(stream.read())

    def dumps(self, reqs, project: RootDependency, content: Optional[str] = None) -> str:
        raise NotImplementedError

    def dump(self, reqs, path, project: RootDependency) -> None:
        # read
        path = Path(str(path))
        if path.exists():
            with path.open('r', encoding='utf8') as stream:
                content = stream.read()
        else:
            content = None

        # make new content
        content = self.dumps(reqs=reqs, content=content, project=project)

        # write
        with path.open('w', encoding='utf8') as stream:
            stream.write(content)

    # resolver creation

    @staticmethod
    def _get_resolver(root: RootDependency) -> Resolver:
        return Resolver(
            graph=Graph(root),
            mutator=Mutator(),
        )

    def loads_resolver(self, content: str) -> Resolver:
        root = self.loads(content)
        return self._get_resolver(root)

    def load_resolver(self, path) -> Resolver:
        root = self.load(path)
        return self._get_resolver(root)

    # helpers

    @staticmethod
    def _get_name(*, path=None, content=None) -> str:
        if path is not None:
            path = Path(str(path))
            file_name = path.name
            project_name = path.parent.name

            if file_name in FILES:
                return project_name
            if file_name[0].isdigit():
                return project_name
            return file_name

        if content is not None:
            return 'root-{length}'.format(length=len(content))

        raise ValueError('please, specify path or content')

    @staticmethod
    def _split_extra_and_marker(text: str) -> Tuple[str, Optional[str]]:
        text = text.lstrip('[').lstrip('[')
        if ':' not in text:
            return text, None
        extra, marker = text.split(':')
        if not extra:
            extra = 'main'
        return extra, None
