class TaskMaxHeap:
    def __init__(self, tasks=None):
        self.heap = []
        self.position_map = {} # {task_id: index_in_heap}
        if tasks:
            for task in tasks:
                self.insert(task)

    def _swap(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]
        self.position_map[self.heap[i].task_id] = i
        self.position_map[self.heap[j].task_id] = j

    def insert(self, task):
        self.heap.append(task)
        idx = len(self.heap) - 1
        self.position_map[task.task_id] = idx
        self._sift_up(idx)

    def _sift_up(self, idx):
        while idx > 0:
            parent = (idx - 1) // 2
            if self.heap[idx].priority_score > self.heap[parent].priority_score:
                self._swap(idx, parent)
                idx = parent
            else:
                break

    def _sift_down(self, idx):
        length = len(self.heap)
        while True:
            largest = idx
            left = 2 * idx + 1
            right = 2 * idx + 2
            if left < length and self.heap[left].priority_score > self.heap[largest].priority_score:
                largest = left
            if right < length and self.heap[right].priority_score > self.heap[largest].priority_score:
                largest = right
            if largest != idx:
                self._swap(idx, largest)
                idx = largest
            else:
                break

    def pop_max(self):
        if not self.heap: return None
        return self.remove_by_id(self.heap[0].task_id)

    def remove_by_id(self, task_id):
        if task_id not in self.position_map:
            return None
        idx = self.position_map[task_id]
        last_idx = len(self.heap) - 1
        
        if idx == last_idx:
            removed = self.heap.pop()
            del self.position_map[task_id]
        else:
            self._swap(idx, last_idx)
            removed = self.heap.pop()
            del self.position_map[task_id]
            # After swap, the new element at 'idx' might need to go up or down
            self._sift_down(idx)
            self._sift_up(idx)
        return removed

    def get_sorted_tasks(self):
        """Returns a list of tasks from highest to lowest priority."""
        # We work on a copy to avoid destroying the original heap
        temp_heap = TaskMaxHeap(self.heap)
        sorted_list = []
        while temp_heap.heap:
            sorted_list.append(temp_heap.pop_max())
        return sorted_list
    
class Stack:
    def __init__(self, tasks=None):
        # Initialize with a copy to avoid side effects if a list is passed
        self.stack = list(tasks) if tasks else []

    def push(self, task):
        self.stack.append(task)

    def pop(self):
        if not self.stack:
            return None
        return self.stack.pop()

    def peek(self):
        if not self.stack:
            return None
        return self.stack[-1]

    def get_task_stack(self):
        """Returns a list of tasks in the order they would be popped (LIFO)."""
        # We slice [::-1] to show the top of the stack first without destroying it
        return self.stack[::-1]