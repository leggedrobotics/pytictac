# TicTac - Time your Torch Code Easily
This repository simplifies timing of code by reducing the amount of boilerplate code needed. 
Specifically, it provides a context manager that can be used to time a block of code. 
The context manager will print the time taken to execute the block of code. 
Additionally, full classes/objects can be timed easily and statistics are generated.


# Installation
```
pip3 install pytictac
```


# Basic Usage

Old:
```python
import torch

def func(x):
    return x*2

start = torch.cuda.Event(enable_timing=True)
end = torch.cuda.Event(enable_timing=True)
start.record()

# Compute
func(2)

end.record()
torch.cuda.synchronize()
print(start.elapsed_time(end))
```

New:
```python
from pytictac import Timer, CpuTimer

def func(x):
    return x*2

# Compute
with Timer("func2"):
    func(2)

with CpuTimer("func2"):
    func(2)
```
Terminal Output:
```shell
Time func2:  0.0655359998345375 ms
```

There exists always a cpu version (using import time; st = time.time()) and a gpu-version (using torch events). 
This is handy when you want to time for example a dataloader where you cannot use torch events.

# Advanced Usage

```python
from pytictac import ClassTimer, ClassContextTimer, accumulate_time


class SmallObject:
    def __init__(self):
        self.x = 3

    @accumulate_time
    def method_a(self):
        self.x += 2


class TestObject:
    def __init__(self):
        self.x = 3
        self.small_obj = SmallObject()

        self.cct = ClassTimer(objects=[self, self.small_obj], names=["Test Object", "Small Object"], enabled=True)

    @accumulate_time
    def method_a(self):
        self.x += 2
        self.small_obj.method_a()

    @accumulate_time
    def method_b(self):
        self.x += 2
        with ClassContextTimer(parent_obj=self, block_name="method_b.1", parent_method_name="method_b"):
            self.x = 3
            with ClassContextTimer(
                parent_obj=self, block_name="method_b.1.a", parent_method_name="method_b.1", n_level=2, cpu=True
            ):
                self.x = 4

    @cpu_accumulate_time
    def method_c(self):
        self.x -= 2

    @cpu_accumulate_time
    def method_d(self):
        self.x = 0

    def __str__(self):
        return self.cct.__str__()


to = TestObject()
to.method_a()
to.method_a()
to.method_a()
to.method_b()
to.method_c()
print(to)
```
Terminal Output:
```shell
Test Object                           total [ms]    count [n]        std [ms]       mean [ms]
  +-  method_a:                       0.16          3                0.045          0.054           
  +-  method_b:                       0.05          1                0.0            0.05            
  +------  method_b.1:                0.03          1                0.0            0.027           
  +-----------  method_b.1.a:         0.01          1                0.0            0.007           
  +-  method_c:                       0.01          1                0.0            0.005           
Small Object                          total [ms]    count [n]        std [ms]       mean [ms]
  +-  method_a:                       0.02          3                0.001          0.005       
```

# Releasing
```
python3 setup.py bdist_wheel 
twine upload dist/* 
```