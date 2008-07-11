import iset

def inplace_encode(asm):
    i = 0
    while i < len(asm):
        insn = iset.INSN_MAP[asm[i]]
        asm[i] = insn.opcode
        i += insn.length
    return asm
    
def encode(asm):
    new_asm = asm[:]
    return inplace_encode(new_asm)
