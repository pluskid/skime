from ..iset   import INSN_MAP
from ..form   import Form
from ..proc   import Procedure

class Builder(object):
    "Builder is a helper of building the bytecode for a form."
    def __init__(self, env, result_t=Form):
        # The lexical environment where the form is compiled
        self.env = env
        # The type of the generate result
        self.result_t = result_t

        # The instruction stream
        self.stream = []
        # The program counter (instruction pointer)
        self.ip = 0
        # The lable name => ip mapping
        self.labels = {}
        # The literals
        self.literals = []
        # The literal name => idx mapping
        self.literals_map = {}

    def emit(self, insn_name, *args):
        "Emit an instruction"
        insn = INSN_MAP.get(insn_name)
        if insn is None:
            raise TypeError, "No such instruction: %s" % insn_name
        if insn.length != 1+len(args):
            raise TypeError, \
                  "INSTRUCTION %s expects %d parameters, but %d given" % \
                  (insn_name, insn.length-1, len(args))
        self.stream.append((insn_name, args))
        self.ip += len(args)+1

    def def_local(self, name):
        "Define a local variable."
        self.env.alloc_local(name)

    def def_label(self, name):
        "Define a label at current ip."
        if self.labels.get(name) is not None:
            raise TypeError, "Duplicated label: %s" % name
        self.labels[name] = self.ip

    def emit_local(self, action, name):
        """\
        Emit an instruction to push or set local variable. The local variable
        is automatically searched in the current context and parents.
        """
        depth, idx = self.find_local_depth(name)
        if depth is None:
            raise UnboundVariable(name, "Unbound variable %s" % name)
        if depth == 0:
            postfix = ''
            args = (idx,)
        else:
            postfix = '_depth'
            args = (depth, idx)
        self.emit('%s_local%s' % (action, postfix), *args)

    def push_proc(self, args=[], rest_arg=False):
        """\
        Return a builder for building a procedure. The returned builder
        is used to build the body of the procedure.

        Later when self.generate is called, builder.generate will be called
        automatically to get the procedure object, add it to the literals
        and push to the operand stack.
        """
        # create a new environment for procedure
        env = Environment(self.env)
        # Define procedure arguments as local variables
        for x in args:
            env.alloc_local(x)

        bdr = Builder(env, result_t=Procedure)
        # Those properties are recorded in the builder and used
        # to construct the procedure later
        bdr.args = args
        bdr.rest_arg = rest_arg

        # generate_proc is a pseudo instruction
        self.stream.append(('generate_proc', bdr))
        
        return bdr

    def generate(self):
        """\
        Generate a form with emitted instructions.
        """
        bc = array('i')
        for insn_name, args in self.stream:
            # pseudo instructions
            if insn_name == 'generate_proc':
                idx = len(self.literals)
                self.literals.append(args.generate())
                bc.append(INSN_MAP['push_literal'].opcode)
                bc.append(idx)
            # real instructions
            else:
                insn = INSN_MAP[insn_name]
                bc.append(insn.opcode)

                if insn_name in ['goto', 'goto_if_false', 'goto_if_not_false']:
                    bc.append(self.labels[args[0]])
                elif insn_name == 'push_literal':
                    idx = self.literal_map.get(args[0])
                    if idx is None:
                        idx = len(self.literals)
                        self.literals.append(args[0])
                        self.literal_map[args[0]] = idx
                    bc.append(idx)
                else:
                    for x in args:
                        bc.append(x)

        return self.result_t(self, bc)

        
    ########################################
    # Helpers used internally
    ########################################
    def find_local_depth(self, name):
        """\
        Find the depth and index of a local variable. If no variable
        with the given name is found, return (None, None).
        """
        depth = 0
        env = self.env
        while env is not None:
            idx = env.find_local(name)
            if idx is not None:
                return (depth, idx)
            depth += 1
            env = env.parent
        return (None, None)
