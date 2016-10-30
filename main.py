#!/usr/bin/env python

from parser import SQLParser

if __name__ == '__main__':
    
    parser = SQLParser()
    parser.parse([
        ('K_SELECT', 'SELECT'),
        ('WS', ' '),
        ('ID', 'name'),
        ('COMMA', ','),
        ('WS', ' '),
        ('ID', 'age'),
        ('WS', '\r\n'),
        ('K_FROM', 'FROM'),
        ('WS', ' '),
        ('ID', 'foo'),
        ('COMMA', ','),
        ('WS', ' '),
        ('ID', 'bar'),
        ('WS', '\r\n'),
        ('K_WHERE', 'WHERE'),
        ('WS', ' '),
        ('NOT', 'NOT'),
        ('WS', ' '),
        ('LPAREN', '('),
        ('ID', 'foo'),
        ('WS', ' '),
        ('RL', '>='),
        ('WS', ' '),
        ('ID', 'bar'),
        ('WS', ' '),
        ('AND', 'AND'),
        ('WS', ' '),
        ('NOT', 'NOT'),
        ('WS', ' '),
        ('LPAREN', '('),
        ('ID', 'foo1'),
        ('WS', ' '),
        ('RL', '<='),
        ('WS', ' '),
        ('ID', 'bar1'),
        ('WS', ' '),
        ('OR', 'OR'),
        ('WS', ' '),
        ('ID', 'foo2'),
        ('WS', ' '),
        ('RL', '<'),
        ('WS', ' '),
        ('ID', 'bar2'),
        ('RPAREN', ')'),
        ('RPAREN', ')')
    ])

    parser.print_parse_tree()

 
