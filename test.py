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
                            "goto_if_true", 18,
                            "push_1",
                            "push_local", 0,
                            "minus",
                            "call", 0, 1,
                            "push_local", 0,
                            "multiply",
                            "goto", 19,
                            "push_1",
                            "ret"])
    proc.literals = ['fact']

    vm.ctx = Context(vm, proc)
    vm.ctx.locals = [5]
    vm.run()
