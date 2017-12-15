import sys
import dis
import pygraphviz

def gcd(a, b):
    if a<b:
        c = a
        a = b
        b = c

    while b != 0 :
        c = a
        a = b
        b = c % b
    return a

def myfn(a,b):
    c = 100
    d = 200
    if a > b:
        d += c
        pass
    else:
        d -= c
    return d

class CFGNode:
    def __init__(self, i, bid):
        self.i = i
        self.bid = bid
        self.children = []
        self.props = {}
    def add_child(self, n): self.children.append(n)


class CFG:
    def __init__(self, myfn):
        def lstadd(hmap, key, val):
            if key not in hmap:
                hmap[key] = [val]
            else:
                hmap[key].append(val)
        enter = CFGNode(dis.Instruction('NOP', opcode=dis.opmap['NOP'], arg=0, argval=0, argrepr=0, offset=0,starts_line=0, is_jump_target=False), 0)
        last = enter
        self.jump_to = {}
        self.opcodes = {}
        for i,ins in enumerate(dis.get_instructions(myfn)):
            byte = i * 2
            node = CFGNode(ins, byte)
            self.opcodes[byte] = node
            print(i,ins)
            if ins.opname in ['LOAD_CONST', 'LOAD_FAST', 'STORE_FAST', 'COMPARE_OP', 'INPLACE_ADD', 'INPLACE_SUBTRACT', 'RETURN_VALUE', 'BINARY_MODULO', 'POP_BLOCK']:
                last.add_child(node)
                last = node
            elif ins.opname == 'POP_JUMP_IF_FALSE':
                print("will jump to", ins.arg)
                lstadd(self.jump_to, ins.arg, node)
                node.props['jmp'] = True
                last.add_child(node)
                last = node
            elif ins.opname == 'JUMP_FORWARD':
                node.props['jmp'] = True
                lstadd(self.jump_to, (i+1)*2 + ins.arg, node)
                print("will jump to", (i+1)*2 + ins.arg)
                last.add_child(node)
                last = node
            elif ins.opname == 'SETUP_LOOP':
                print("setuploop: ", byte , ins.arg)
                last.add_child(node)
                last = node
            elif ins.opname == 'JUMP_ABSOLUTE':
                print("will jump to", ins.arg)
                lstadd(self.jump_to, ins.arg, node)
                node.props['jmp'] = True
                last.add_child(node)
                last = node
            else:
                assert False
        for byte in self.opcodes:
            if  byte in self.jump_to:
                node = self.opcodes[byte]
                assert node.i.is_jump_target
                for b in self.jump_to[byte]:
                    b.add_child(node)

    def to_graph(self):
        G = pygraphviz.AGraph(directed=True)
        for nid, cnode in self.opcodes.items():
            G.add_node(cnode.bid)
            n = G.get_node(cnode.bid)
            n.attr['label'] = "%d: %s" % (nid, cnode.i.opname)
            for cn in cnode.children:
                G.add_edge(cnode.bid, cn.bid)
        return G


def main():
    dis.dis(gcd)
    v = CFG(gcd)
    g = v.to_graph()
    g.draw('out.png', prog='dot')
if __name__ == '__main__':
    main()
