import torch
import time
from functools import wraps


class BlockTimeInfo:
    def __init__(self, block_name, n_level=0, parent_method_name=None):
        self.block_name = block_name
        self.time = 0
        self.time_squared = 0
        self.n = 0
        self.n_level = n_level
        self.parent_method_name = None

    def compute(self):
        mean = self.time / self.n
        std = round(((self.time_squared / self.n) - (mean**2)) ** 0.5, 3)
        return mean, std

    def update(self, time):
        self.time += time
        self.time_squared += time**2
        self.n += 1


class ClassContextTimer:
    def __init__(self, parent_obj, block_name="", parent_method_name=None, n_level=1, cpu=False) -> None:
        self.parent_obj = parent_obj

        if not hasattr(self.parent_obj, "ct_enabled"):
            return
        elif not self.parent_obj.ct_enabled:
            return

        block_time_info = None
        for info in parent_obj.ct_block_times:
            # This may be inefficient for large number of methods
            if info.block_name == block_name:
                block_time_info = info
                break
        if block_time_info is None:
            block_time_info = BlockTimeInfo(block_name, parent_method_name=parent_method_name, n_level=n_level)
            parent_obj.ct_block_times.append(block_time_info)

        self.block_time_info = block_time_info
        if not cpu:
            self.start = torch.cuda.Event(enable_timing=True)
            self.end = torch.cuda.Event(enable_timing=True)
        self.cpu = cpu

    def __enter__(self):
        if not self.parent_obj.ct_enabled:
            return

        self.tic()

    def __exit__(self, exc_type, exc_value, exc_tb):
        if not self.parent_obj.ct_enabled:
            return

        st = self.toc()
        self.block_time_info.update(st)

    def tic(self):
        if self.cpu:
            self.start = time.time()
        else:
            self.start.record()

    def toc(self):
        if self.cpu:
            return (time.time() - self.start)*1000

        self.end.record()
        torch.cuda.synchronize()
        return self.start.elapsed_time(self.end)


class ClassTimer:
    def __init__(self, objects, names, enabled=True) -> None:
        self.objects = objects
        self.names = names

        for o in self.objects:
            o.ct_enabled = enabled
            o.ct_block_times = []

    def enable(self):
        for o in self.objects:
            o.ct_enabled = True

    def disable(self):
        for o in self.objects:
            o.ct_enabled = False

    def reset(self):
        for o in self.objects:
            o.ct_block_times = []

    def __str__(self):
        s = ""

        for n, o in zip(self.names, self.objects):
            s += n.ljust(38) + "total [ms]" + " " * 4 + "count [n]" + " " * 8 + "std [ms]" + " " * 7 + "mean [ms]\n"

            entries = []
            for info in o.ct_block_times:
                spacing = int(info.n_level * 5)
                mean, std = info.compute()

                entries.append(
                    "  +"
                    + "-" * spacing
                    + f"-  {info.block_name}:".ljust(35 - spacing)
                    + f"{round(info.time,2)}".ljust(14)
                    + f"{info.n} ".ljust(16)
                    + f" {std}".ljust(16)
                    + f"{round(mean,3)}".ljust(16)
                )

            # Sort the entries according to there level and the parent_method_name.
            entries_level_n = [(e, info.block_name) for e, info in zip(entries, o.ct_block_times) if info.n_level == 0]
            if len(o.ct_block_times) != 0:
                max_level = max([info.n_level for info in o.ct_block_times])
                for n in range(1, max_level + 1):
                    for e, info in zip(entries, o.ct_block_times):
                        if info.n_level == n:
                            for j, (_, block_name) in enumerate(entries_level_n):
                                if block_name == info.parent_method_name:
                                    break
                            entries_level_n = entries_level_n[:j] + [(e, info.block_name)] + entries_level_n[j:]

                entries_level_n = [e for e, _ in entries_level_n]

                s += "\n".join(entries_level_n)
            s += "\n"

        if len(s) == 0:
            s = "Not timeings were recorded. Did you use the decorator @accumulate_time and call the methods?\n"

        return s[:-1]


def accumulate_time(method):
    @wraps(method)
    def timed(*args, **kw):
        if not hasattr(args[0], "ct_enabled"):
            return method(*args, **kw)
        elif not args[0].ct_enabled:
            return method(*args, **kw)

        start = torch.cuda.Event(enable_timing=True)
        end = torch.cuda.Event(enable_timing=True)
        start.record()
        result = method(*args, **kw)
        end.record()
        torch.cuda.synchronize()
        st = start.elapsed_time(end)

        block_time_info = None
        for info in args[0].ct_block_times:
            # This may be inefficient for large number of methods
            if info.block_name == method.__name__:
                block_time_info = info
                break
        if block_time_info is None:
            block_time_info = BlockTimeInfo(method.__name__)
            args[0].ct_block_times.append(block_time_info)

        block_time_info.update(st)
        return result

    return timed


def cpu_accumulate_time(method):
    @wraps(method)
    def timed(*args, **kw):
        if not hasattr(args[0], "ct_enabled"):
            return method(*args, **kw)
        elif not args[0].ct_enabled:
            return method(*args, **kw)

        st = time.time()
        result = method(*args, **kw)
        # Convert to ms
        st = (time.time() - st) * 1000

        block_time_info = None
        for info in args[0].ct_block_times:
            # This may be inefficient for large number of methods
            if info.block_name == method.__name__:
                block_time_info = info
                break
        if block_time_info is None:
            block_time_info = BlockTimeInfo(method.__name__)
            args[0].ct_block_times.append(block_time_info)

        block_time_info.update(st)
        return result

    return timed
