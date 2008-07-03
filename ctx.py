
class Context(object):
    def __init__(self, vm, proc):
        self.vm = vm
        self.parent = vm.ctx
        self.proc = proc
        
        self.ip = 0
        self.bytecode = proc.bytecode
