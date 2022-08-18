import helper

class TestCallCc(object):
    def eval(self, vm, code):
        compiler = helper.Compiler()
        proc = compiler.compile(helper.parse(code), vm.env)
        return vm.run(proc)

    def test_call_cc(self):
        vm = helper.VM()

        self.eval(vm, "(define return #f)")
        assert self.eval(vm, """
        (+ 1 (call/cc
               (lambda (cont)
                 (set! return cont)
                 1)))""") == 2
        assert self.eval(vm, "(return 22)") == 23
        
        
