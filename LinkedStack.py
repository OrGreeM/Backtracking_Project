"""
Implementation of Stack ADT using linked list
"""


class Stack:
    """Simple stack implementation using linked nodes."""

    def __init__(self):
        """Create an empty stack."""
        self._top = None
        self._size = 0

    def is_empty(self):
        """Return True if the stack is empty."""
        return self._top is None

    def __len__(self):
        """Return number of items in the stack."""
        return self._size

    def peek(self):
        """Return top item without removing it."""
        assert not self.is_empty(), "Cannot peek at an empty stack"
        return self._top.item

    def pop(self):
        """Remove and return the top item."""
        assert not self.is_empty(), "Cannot pop from an empty stack"
        node = self._top
        self._top = self._top.next
        self._size -= 1
        return node.item

    def push(self, item):
        """Push item onto the stack."""
        self._top = _StackNode(item, self._top)
        self._size += 1


class _StackNode:
    """Node used internally by Stack."""

    def __init__(self, item, link):
        self.item = item
        self.next = link
