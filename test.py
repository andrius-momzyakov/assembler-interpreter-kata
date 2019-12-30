import unittest
from asm import assembler_interpreter


class MyTestCase1(unittest.TestCase):

    def test(self):
        program = '''
        ; My first program
        mov  a, 5
        inc  a
        call function
        msg  '(5+1)/2 = ', a    ; output message
        end

        function:
            div  a, 2
            ret
        '''
        self.assertEqual(assembler_interpreter(program), '(5+1)/2 = 3')


class MyTestCase2(unittest.TestCase):

    def test(self):
        program_factorial = '''
        mov   a, 5
        mov   b, a
        mov   c, a
        call  proc_fact
        call  print
        end

        proc_fact:
            dec   b
            mul   c, b
            cmp   b, 1
            jne   proc_fact
            ret

        print:
            msg   a, '! = ', c ; output text
            ret
        '''

        self.assertEqual(assembler_interpreter(program_factorial), '5! = 120')


class MyTestCase3(unittest.TestCase):

    def test(self):
        program_mod = '''
        mov   a, 11           ; value1
        mov   b, 3            ; value2
        call  mod_func
        msg   'mod(', a, ', ', b, ') = ', d        ; output
        end

        ; Mod function
        mod_func:
            mov   c, a        ; temp1
            div   c, b
            mul   c, b
            mov   d, a        ; temp2
            sub   d, c
            ret
        '''
        self.assertEqual(assembler_interpreter(program_mod), 'mod(11, 3) = 2')


class MyTestCase4(unittest.TestCase):

    def test(self):
        program_fail = '''
        call  func1
        call  print
        end

        func1:
            call  func2
            ret

        func2:
            ret

        print:
            msg 'This program should return -1'
        '''
        self.assertEqual(assembler_interpreter(program_fail), -1)


if __name__ == '__main__':
    unittest.main()

