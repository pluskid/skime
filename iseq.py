def op_ret(ctx):
    ctx.vm.ret()

def op_call(ctx):
    proc_name = get_param(1)
    argc = get_param(2)

def op_push_local(ctx):
    pass

def op_push_literal(ctx):
    idx = get_param(ctx, 1)
    lit = ctx.proc.literals[idx]
    ctx.vm.stk_push(lit)
    
def op_push_0(ctx):
    ctx.vm.stk_push(0)

def op_push_1(ctx):
    ctx.vm.stk_push(1)

def op_dup(ctx):
    ctx.vm.stk_push(ctx.vm.stk_top())

def op_plus(ctx):
    res = ctx.vm.stk_pop() + ctx.vm.stk_pop()
    ctx.vm.stk_push(res)

def op_minus(ctx):
    res = ctx.vm.stk_pop() - ctx.vm.stk_pop()
    ctx.vm.stk_push(res)

def op_multiply(ctx):
    res = ctx.vm.stk_pop() * ctx.vm.stk_pop()
    ctx.vm.stk_push(res)

def op_divide(ctx):
    res = ctx.vm.stk_pop() / ctx.vm.stk_pop()
    ctx.vm.stk_push(res)

def op_equal(ctx):
    res = (ctx.vm.stk_pop() == ctx.vm.stk_pop())
    ctx.vm.stk_push(res)

def op_goto(ctx):
    ip = get_param(ctx, 1)
    ctx.ip = ip

def op_goto_if_true(ctx):
    ip = get_param(ctx, 1)
    cond = ctx.vm.stk_pop()
    if cond is True:
        ctx.ip = ip
    else:
        ctx.ip += 2 # insn length = 2

def op_goto_if_not_true(ctx):
    ip = get_param(ctx, 1)
    cond = ctx.vm.stk_pop()
    if cond is not True:
        ctx.ip = ip
    else:
        ctx.ip += 2 # insn length = 2

def op_push_local(ctx):
    idx = get_param(ctx, 1)
    loc = ctx.proc.locals[idx]
    ctx.vm.stk_push(loc)

def op_set_local(ctx):
    idx = get_param(ctx, 1)
    val = ctx.vm.stk_pop()
    ctx.proc.locals[idx] = val

# Instruction Tags
TAG_NORMAL = 0
TAG_CTL_FLOW = 1

INSNS = [
    # length  name                action               tag
    ( 1,      "ret",              op_ret,              TAG_NORMAL),
    ( 3,      "call",             op_call,             TAG_NORMAL),
    ( 2,      "goto",             op_goto,             TAG_NORMAL),
    ( 2,      "push_local",       op_push_local,       TAG_NORMAL),
    ( 1,      "push_0",           op_push_0,           TAG_NORMAL),
    ( 1,      "push_1",           op_push_1,           TAG_NORMAL),
    ( 2,      "push_literal",     op_push_literal,     TAG_NORMAL),
    ( 1,      "dup",              op_dup,              TAG_NORMAL),
    ( 1,      "plus",             op_plus,             TAG_NORMAL),
    ( 1,      "minus",            op_minus,            TAG_NORMAL),
    ( 1,      "multiply",         op_multiply,         TAG_NORMAL),
    ( 1,      "divide",           op_divide,           TAG_NORMAL),
    ( 1,      "equal",            op_equal,            TAG_NORMAL),
    ( 2,      "goto",             op_goto,             TAG_CTL_FLOW),
    ( 2,      "goto_if_true",     op_goto_if_true,     TAG_CTL_FLOW),
    ( 2,      "goto_if_not_true", op_goto_if_not_true, TAG_CTL_FLOW),
    ( 2,      "push_local",       op_push_local,       TAG_NORMAL),
    ( 2,      "set_local",        op_set_local,        TAG_NORMAL)
    ]

def run(vm):
    ctx = vm.ctx
    while ctx.ip < len(ctx.bytecode):
        opcode = ctx.bytecode[ctx.ip]
        insn_action(opcode)(ctx)
        if not has_tag(opcode, TAG_CTL_FLOW):
            ctx.ip = ctx.ip + insn_length(opcode) 

        

def insn_length(insn):
    return INSNS[insn][0]

def insn_action(insn):
    return INSNS[insn][2]

def insn_tag(insn):
    return INSNS[insn][3]

def get_param(ctx, n):
    return ctx.bytecode[ctx.ip+n]

def has_tag(opcode, tag):
    return (insn_tag(opcode) & tag) == tag
