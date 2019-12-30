import re

def assembler_interpreter(program):
    program = program.splitlines()
    k = 0
    while k < len(program):
        program[k] = re.sub(r'(\s*;[\s]*.*)', '', program[k])  # cut off comments
        if program[k] is None or program[k].strip() == '':
            del program[k]
            continue
        program[k] = program[k].strip()
        k += 1

    pointer = [0]
    regs = {}
    output = ['']
    labels = {}
    cmp_regs = []
    end_flag = [False]

    def set_label(lab, offset, labels=labels):
        if labels.get(lab) is not None:
            print('duplicate label!')
            return -1
        labels[lab] = offset  # idx in prod arr where lab set

    def labels_setter(prog=program):
        idx = 0
        for l in prog:
            r = re.match(r'([a-z$_]+[a-z$_0-9]*):', l)
            if r:
                label = r.group(1)
                res = set_label(label, idx)
                if res == -1:
                    return -1
            idx += 1

    res = labels_setter()
    if res == -1:
        return -1

    def mov_pointer(steps=1, pointer=pointer):
        pointer[0] += steps

    def msg(cmd, regs=regs, output=output):
        params = re.sub(r'^msg\s+', '', cmd)
        params = re.findall(r"'[^']*'|[0-9a-z]+", params)
        s = ''
        for i in params:
            if "'" in i:
                val = i.strip()
                val = val.replace("'", '')
                s = s + val
            else:
                reg = i.strip()
                val = str(regs[reg])
                val = val.strip()
                s = s + val
        output[0] += s
        mov_pointer()

    def mov_pointer_abs(idx, pointer=pointer):
        pointer[0] = idx

    def mov(reg, val, regs=regs):
        regs[reg] = int(val)
        mov_pointer()

    def mov2(reg, reg2, regs=regs):
        regs[reg] = regs[reg2]
        mov_pointer()

    def inc(reg, regs=regs):
        regs[reg] = regs[reg] + 1
        mov_pointer()

    def dec(reg, regs=regs):
        regs[reg] -= 1
        mov_pointer()

    def jnz(reg, n, regs=regs):
        if regs.get(reg) is None:
            print('register {} not initialized. command skipped.'.format(reg))
            return -1
        else:
            if regs[reg] != 0:
                mov_pointer(steps=int(n))
                return
            mov_pointer()

    def jnz2(val, n):
        if val is None:
            print('value {} not initialized. command skipped.'.format(val))
            return -1
        else:
            val = int(val)
            if val != 0:
                mov_pointer(steps=int(n))
                return
            mov_pointer()

    def aop(op, reg, val, regs=regs):
        if re.search(r'[a-z]', val):
            val = regs[val]
        if op == 'add':
            regs[reg] += int(val)
        elif op == 'sub':
            regs[reg] -= int(val)
        elif op == 'mul':
            regs[reg] *= int(val)
        elif op == 'div':
            val = int(val)
            if val == 0:
                print('divizion by zero!')
                return -1
            res = int(regs[reg] / int(val))
            regs[reg] = res
        mov_pointer()

    def pass_lbl():
        mov_pointer()

    def jmp(label, labels=labels):
        idx = labels[label]
        mov_pointer_abs(idx)

    def cmp(x, y, cmp_regs=cmp_regs):
        if re.match(r'(-?[0-9]+)', x):
            x = int(x)
        else:
            x = regs[x]
        if re.match(r'(-?[0-9]+)', y):
            y = int(y)
        else:
            y = regs[y]

        del cmp_regs[:]

        if x == y:
            cmp_regs.append('e')
        if x <= y:
            cmp_regs.append('le')
        if x < y:
            cmp_regs.append('l')
        if x >= y:
            cmp_regs.append('ge')
        if x > y:
            cmp_regs.append('g')
        if x != y:
            cmp_regs.append('ne')
        mov_pointer()

    def jcmp(case, label, labels=labels, cmp_regs=cmp_regs):
        if case in cmp_regs:
            idx = labels[label]
            mov_pointer_abs(idx)
        mov_pointer()

    stack = []

    def call(label, labels=labels, stack=stack, pointer=pointer):
        stack.insert(0, pointer[0] + 1)  # ret will move to next instr after call
        idx = labels[label]
        mov_pointer_abs(idx)

    def ret(stack=stack):
        idx = stack.pop(0)
        mov_pointer_abs(idx)

    def end(end_flag=end_flag):
        end_flag[0] = True

    def interpret(cmd):
        tokens = [
            (r'mov\s+(?P<reg>[0-9a-z]+)\s*,\s*(?P<val>\d+)', mov),
            (r'mov\s+(?P<reg>[0-9a-z]+)\s*,\s*(?P<reg2>[a-z]+)', mov2),
            (r'inc\s+(?P<reg>[0-9a-z]+)', inc),
            (r'dec\s+(?P<reg>[0-9a-z]+)', dec),
            (r'jnz\s+(?P<reg>[a-z]+) (?P<n>\-?\d+)', jnz),
            (r'jnz\s+(?P<val>\-?\d+) (?P<n>\-?\d+)', jnz2),

            (r'(?P<op>add|sub|mul|div)\s+(?P<reg>[0-9a-z]+)\s*,\s*(?P<val>-?\d+|[0-9a-z]+)', aop),

            (r'[a-z$_][a-z$_0-9]*:', pass_lbl),
            (r'jmp\s+(?P<label>[a-z$_]+[a-z$_0-9]*)', jmp),

            (r'cmp\s+(?P<x>-?[0-9]+|[a-z]+)\s*,\s*(?P<y>-?[0-9]+|[a-z]+)', cmp),
            (r'j(?P<case>ne|e|g|ge|l|le)\s+(?P<label>[a-z$_]+[a-z$_0-9]*)', jcmp),

            (r'call\s+(?P<label>[a-z$_][a-z$_0-9]*)', call),
            (r'ret', ret),
            (r'(?P<cmd>msg\s+.+)', msg),
            (r'end', end)
        ]
        import re
        for token in tokens:
            r = re.match(token[0], cmd)
            if r:
                args = r.groups()
                res = token[1](*args)
                return res
        print('Invalid command. Cancelled.')
        return -1

    p_size = len(program)
    if p_size == 0:
        return regs
    while pointer[0] < p_size:
        cmd = program[pointer[0]]
        res = interpret(cmd)
        if end_flag[0]:
            break
        if res == -1:
            return -1
        if pointer[0] >= 0 and pointer[0] < p_size:
            pass
        elif pointer[0] == p_size:
            break
        else:
            print('Pointer is out of program. Cancelled.')
            break
    if not end_flag[0]:
        return -1
    # return a dictionary with the registers
    return output[0]
