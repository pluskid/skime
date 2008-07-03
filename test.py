from vm import VM
from ctx import Context
from proc import Procedure
from codec import encode

if __name__ == '__main__':
    vm = VM()

    proc = Procedure()
    proc.bytecode = encode(["push_local", 0,
                            "push_1",
                            "equal",
                            "goto_if_true", 21,
                            "push_local", 1,
                            "push_local", 0,
                            "multiply",
                            "set_local", 1,
                            "push_1",
                            "push_local", 0,
                            "minus",
                            "set_local", 0,
                            "goto", 0,
                            "push_local", 1])
    proc.literals = [10, 5.5, 55]
    proc.locals = [5, 1]

    vm.ctx = Context(vm, proc)
    vm.run()
    print vm.stk_top()
