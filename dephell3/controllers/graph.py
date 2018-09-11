from logging import getLogger


logger = getLogger(__name__)


class Graph:
    def __init__(self, root):
        self.root = root
        self.reset()

    def reset(self):
        self.mapping = {self.root.name: self.root}
        self.conflict = None

    def get_leafs(self) -> tuple:
        return tuple(dep for dep in self.mapping.values() if not dep.applied)

    def get_children(self, dep, *, graph=True, layers=None) -> dict:
        if not dep.locked:
            return dict()
        if layers is not None:
            layers -= 1

        result = dict()
        for child in dep.dependencies:
            if graph and child.normalized_name not in self.mapping:
                continue
            if child.normalized_name in result:
                logger.warning('Recursive dependency: {}'.format(child))
            else:
                result[child.normalized_name] = child
            if layers != 0:
                result.update(self.get_children(child, layers=layers))
        return result

    def get_parents(self, dep, *, layers=None) -> dict:
        parents = dict()
        for parent in self.mapping.values():
            if dep.normalized_name in self.get_children(parent, layers=layers):
                parents[dep.normalized_name] = dep
        return parents
