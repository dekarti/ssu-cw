#!/usr/bin/env python

from treelib import Node, Tree
import uuid

class SQLParser(object):
    def __init__(self):
        self.parse_tree = Tree()
        self.query = ''
        self.tokens = []
        self.current_position = 0

    def __next_token(self):
        if self.current_position >= len(self.tokens):
            return None, None
        token = self.tokens[self.current_position]
        #print "Processing token '{}' on position {}".format(
        #        token, self.current_position)
        self.current_position += 1
        return token

    def __leave_repr(self, token):
        t = '000' + str(self.current_position)
        token_class, lexeme = token
        return "{}-{}: {}".format(t[-3:], token_class, lexeme)
    
    def __node_repr(self, nonterminal):
        t = '000' + str(self.current_position)
        return "{}-{}".format(t[-3:], nonterminal)
        
    def __create_subtree(self, nonterminal):
        tree = Tree()
        id = uuid.uuid1()
        tree.create_node(self.__node_repr(nonterminal), id)
        return tree, id 

    def __create_leave_node(self, token):
        tree = Tree()
        id = uuid.uuid1()
        tree.create_node(self.__leave_repr(token), id)
        return tree, id

    def __rollback(self, n):
        self.current_position -= n

    def __is_parsed(self):
        return self.current_position >= len(self.tokens)

    def parse_terminal(self, parent_tree, parent_node, terminal):
        token = self.__next_token()
        token_class, lexeme = token
        if token_class == None:
            return False, 0
        if token_class == terminal:
            tree, id  = self.__create_leave_node(token)
            parent_tree.paste(parent_node, tree)
            return True, 1
        return False, 1
    
    def parse_cond(self, parent_tree, parent_node):
        """
        Defines production rule COND:
        COND -> ID RL ID
        """
        tree, id = self.__create_subtree("cond")

        is_id_parsed, n1 = self.parse_terminal(tree, id, 'ID')
        is_relation_parsed, n2 = self.parse_terminal(tree, id, 'RL')
        is_id_parsed, n3 = self.parse_terminal(tree, id, 'ID')
        
        if is_id_parsed and is_relation_parsed and is_id_parsed:
            parent_tree.paste(parent_node, tree)
            return True, n1+n2+n3
        return False, n1+n2+n3

    def parse_expr(self, parent_tree, parent_node):
        """
        Defines production rule EXPR:
        EXPR -> COND
              | ( EXPR )
              | NOT EXPR
              | COND AND EXPR
              | COND OR EXPR
        """
        if self.__is_parsed():
            return True, 0
        tree, id = self.__create_subtree('expr')
        is_cond_parsed, n1 = self.parse_cond(tree, id)
        is_and_parsed, n2 = self.parse_terminal(tree, id, 'AND')
        is_expr_parsed, n3 = self.parse_expr(tree, id)
        if is_cond_parsed and is_and_parsed and is_expr_parsed:
            parent_tree.paste(parent_node, tree)
            return True, n1+n2+n3
        self.__rollback(n1+n2+n3)
        
        tree, id = self.__create_subtree('expr')
        is_cond_parsed, n1 = self.parse_cond(tree, id)
        is_or_parsed, n2 = self.parse_terminal(tree, id, 'OR')
        is_expr_parsed, n3 = self.parse_expr(tree, id)
        if is_cond_parsed and is_or_parsed and is_expr_parsed:
            parent_tree.paste(parent_node, tree)
            return True, n1+n2+n3
        self.__rollback(n1+n2+n3)

        tree, id = self.__create_subtree('expr')
        is_lparen_parsed, n1 = self.parse_terminal(tree, id, 'LPAREN')
        is_expr_parsed, n2 = self.parse_expr(tree, id)
        is_rparen_parsed, n3 = self.parse_terminal(tree, id, 'RPAREN') 
        if is_lparen_parsed and is_expr_parsed and is_rparen_parsed:
            parent_tree.paste(parent_node, tree)
            return True, n1+n2+n3
        self.__rollback(n1+n2+n3)
        
        tree, id = self.__create_subtree('expr')
        is_not_parsed, n1 = self.parse_terminal(tree, id, 'NOT')
        is_expr_parsed, n2 = self.parse_expr(tree, id)
        if is_not_parsed and is_expr_parsed:
            parent_tree.paste(parent_node, tree)
            return True, n1+n2
        self.__rollback(n1+n2)

        tree, id = self.__create_subtree('expr')
        is_cond_parsed, n1 = self.parse_cond(tree, id)
        if is_cond_parsed:
            parent_tree.paste(parent_node, tree)
            return True, n1
        
        self.__rollback(n1)
        return False, 0

    def parse_where(self, parent_tree, parent_node):


    def parse(self, tokens):
        self.tokens = filter(lambda x: x[0] != 'WS', tokens)
        self.current_position = 0
        self.parse_tree.create_node("".join(list([x[1] for x in tokens])), 'root')
        self.parse_expr(self.parse_tree, 'root')  


    def print_parse_tree(self):
        print "\r\n\r\n"
        self.parse_tree.show()
        print "Current position is {}".format(self.current_position)


if __name__ == '__main__':
    
    parser = SQLParser()
    parser.parse([
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
    #parser.parse('select name from students where age >= 15')
    parser.print_parse_tree()
    
