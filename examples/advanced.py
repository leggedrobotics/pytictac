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
                parent_obj=self, block_name="method_b.1.a", parent_method_name="method_b.1", n_level=2
            ):
                self.x = 4

    @accumulate_time
    def method_c(self):
        self.x -= 2

    @accumulate_time
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

to.cct.reset()
to.cct.disable()
to.cct.enable()
