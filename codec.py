import iseq

class Instruction(object):
    def __init__(self, opcode, data):
        self.opcode = opcode
        self.name = data[1]
        self.length = data[0]
        self.tag = data[3]
        
INSN_MAP = {}
for i in range(len(iseq.INSNS)):
    insn = Instruction(i, iseq.INSNS[i])
    INSN_MAP[insn.name] = insn

def inplace_encode(asm):
    i = 0
    while i < len(asm):
        insn = INSN_MAP[asm[i]]
        asm[i] = insn.opcode
        i += insn.length
    return asm
    
def encode(asm):
    new_asm = asm[:]
    return inplace_encode(new_asm)
