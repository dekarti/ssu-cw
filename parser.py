#
# SELECT -> K_SELECT K_WILDCARD ;
#         | K_SELECT K_WILDCARD 
#         | K_SELECT K_WILDCARD K_FROM SELECT
#         | ( SELECT )
# K_SELECT -> S E L E C T
# K_WILDCARD -> *
#
# EXP   -> ID OP ID
#        | ( EXP )
# a <= 5
# ID        -> WORD
#            | WORD DIGIT
#            |  
#
# WORD      -> LETTER WORD
#            | LETTER
#
# LETTER    -> a | b | .. | z
#
# DIGIT     ->  0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9
from treelib import Node, Tree
import uuid

class SQLParser(object):
    def __init__(self):
        self.parse_tree = Tree()
        self.query = ''
        self.tokens = []
        self.current_position = 0

    def __next_token(self):
        token = self.tokens[self.current_position]
        print "Processing token '{}' on position {}".format(token, self.current_position)
        self.current_position += 1
        return token

    def __create_subtree(self, token, type_):
        tree = Tree()
        id = uuid.uuid1()
        t = '000' + str(self.current_position) 
        tree.create_node("{}: {}".format(t[-3:] + '-' + type_, token), id)
        return tree, id 

    def __rollback(self, n):
        self.current_position -= n

    def __is_parsed(self):
        return len(self.tokens) == self.current_position 

    def parse_ws(self, parent_tree, parent_node):
        """
        Define production rule WS:
        WS -> ' '  | \r | \t
        """
        token = self.__next_token()
        tree, id = self.__create_subtree(token, "ws")

        if token in [' ', '\n', '\r']:
            parent_tree.paste(parent_node, tree)
            return True, 1
        return False, 1

    def parse_wss(self, parent_tree, parent_node):
        """
        Define production rule WSS:
        WSS -> WS WSS | WS
        """
        if self.__is_parsed():
            return True, 0
        token = ""
        tree, id = self.__create_subtree(token, "wss")

        is_ws_parsed, n1 = self.parse_ws(tree, id)
        is_wss_parsed, n2 = self.parse_wss(tree, id)

        if is_ws_parsed:
            if is_wss_parsed:
                parent_tree.paste(parent_node, tree)
                return True, n1+n2
            self.__rollback(n2)
            parent_tree.paste(parent_node, tree)
            return True, n1
        return False, n1
         
    def parse_digit(self, parent_tree, parent_node):
        """
        Defines production rule DIGIT:
        DIGIT -> 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9
        """
        token = self.__next_token()
        tree, id = self.__create_subtree(token,
			 "digit")
        if token.isdigit():
            parent_tree.paste(parent_node, tree)
            return True, 1
        return False, 1 
    
    def parse_letter(self, parent_tree, parent_node):
        """
        Defines production rule LETTER:
        LETTER    -> a | .. | z
        """
        token = self.__next_token()
        tree, id = self.__create_subtree(token,
			 "letter")
        if token.isalpha():
            parent_tree.paste(parent_node, tree)
            return True, 1
        return False, 1

    def parse_eq(self, parent_tree, parent_node):
        """
        Defines production rule EQ:
        EQ -> =
        """
        token = self.__next_token()
        tree, id = self.__create_subtree(token,
                "eq")
        if token == '=':
            parent_tree.paste(parent_node, tree)
            return True, 1
        return False, 1

    def parse_less(self, parent_tree, parent_node):
        """
        Defines production rule LESS:
        LESS -> <
        """
        token = self.__next_token()
        tree, id = self.__create_subtree(token,
                "less")
        if token == '<':
            parent_tree.paste(parent_node, tree)
            return True, 1
        return False, 1
    
    def parse_greater(self, parent_tree, parent_node):
        """
        Defines production rule GREATER:
        GREATER -> >
        """
        token = self.__next_token()
        tree, id = self.__create_subtree(token,
                "greater")
        if token == '>':
            parent_tree.paste(parent_node, tree)
            return True, 1
        return False, 1

    def parse_less_or_eq(self, parent_tree, parent_node):
        """
        Defines production rule LESS_OR_EQ:
        LESS_OR_EQ -> LESS EQ
        """
        token = ""
        tree, id = self.__create_subtree(token,
                "less_or_eq")
        is_less_parsed, n1 = self.parse_less(tree, id)
        is_eq_parsed, n2 = self.parse_eq(tree, id)

        if is_less_parsed and is_eq_parsed:
            parent_tree.paste(parent_node, tree)
            return True, n1+n2
        return False, n1+n2   

    def parse_greater_or_eq(self, parent_tree, parent_node):
        """
        Defines production rule GREATER_OR_EQ:
        GREATER_OR_EQ -> LESS EQ
        """
        token = ""
        tree, id = self.__create_subtree(token,
                "greater_or_eq")
        is_greater_parsed, n1 = self.parse_greater(tree, id)
        is_eq_parsed, n2 = self.parse_eq(tree, id)

        if is_greater_parsed and is_eq_parsed:
            parent_tree.paste(parent_node, tree)
            return True, n1+n2
        return False, n1+n2   
            
    def parse_not_eq(self, parent_tree, parent_node):
        """
        Defines production rule NOT_EQ:
        NOT_EQ -> LESS GREATER
        """
        token = ""
        tree, id = self.__create_subtree(token,
                "not_eq")
        is_less_parsed, n1 = self.parse_less(tree, id)
        is_greater_parsed, n2 = self.parse_greater(tree, id)

        if is_less_parsed and is_greater_parsed:
            parent_tree.paste(parent_node, tree)
            return True, n1+n2
        return False, n1+n2   

    def parse_relation(self, parent_tree, parent_node):
        """
        Defines production RELATION:
        RELATION -> LESS | GREATER | EQ | LESS_OR_EQ | GREATER_OR_EQ | NOT_EQ
        """
        token = ""
        tree, id = self.__create_subtree(token,
                "relation")

        is_less_or_eq_parsed, n1 = self.parse_less_or_eq(tree, id)
        if is_less_or_eq_parsed:
            parent_tree.paste(parent_node, tree)
            return True, n1

        self.__rollback(n1)
        is_greater_or_eq_parsed, n2 = self.parse_greater_or_eq(tree, id)
        if is_greater_or_eq_parsed:
            parent_tree.paste(parent_node, tree)
            return True, n2

        self.__rollback(n2)
        is_not_eq_parsed, n3 = self.parse_not_eq(tree, id)
        if is_not_eq_parsed:
            parent_tree.paste(parent_node, tree)
            return True, n3

        self.__rollback(n3)
        is_less_parsed, n4 = self.parse_less(tree, id)
        if is_less_parsed:
            parent_tree.paste(parent_node, tree)
            return True, n4

        self.__rollback(n4)
        is_greater_parsed, n5 = self.parse_greater(tree, id)
        if is_greater_parsed:
            parent_tree.paste(parent_node, tree)
            return True, n5

        self.__rollback(n5)
        is_eq_parsed, n6 = self.parse_eq(tree, id)
        if is_eq_parsed:
            parent_tree.paste(parent_node, tree)
            return True, n6

        return False, n6
  
    def parse_word(self, parent_tree, parent_node):
        """
        Defines production rule WORD:
        WORD -> LETTER | LETTER WORD
        """
        if self.__is_parsed():
            return True, 0
        token = ""
        tree, id = self.__create_subtree(token,
			 "word")
        is_letter_parsed, n1 = self.parse_letter(tree, id)
        is_word_parsed, n2 = self.parse_word(tree, id)

        if (is_letter_parsed and is_word_parsed):
            parent_tree.paste(parent_node, tree)
            return True, n1+n2
        else:
            self.__rollback(n1+n2)
            tree, id = self.__create_subtree(token,
			 "word")
            is_letter_parsed, n = self.parse_letter(tree, id)
            if (is_letter_parsed):
                parent_tree.paste(parent_node, tree)
                return True, n
        return False, n
 
    def parse_integer(self, parent_tree, parent_node):
        """
        Defines production rule INTEGER:
        INTEGER -> DIGIT INTEGER | INTEGER
        """
        if self.__is_parsed():
            return True, 0
        token = ""
        tree, id = self.__create_subtree(token,
			 "integer")
        is_digit_parsed, n1 = self.parse_digit(tree, id)
        is_integer_parsed, n2 = self.parse_integer(tree, id)

        if (is_digit_parsed and is_integer_parsed):
            parent_tree.paste(parent_node, tree)
            return True, n1+n2
        else:
            self.__rollback(n1+n2)
            tree, id = self.__create_subtree(token,
			 "integer")
            is_digit_parsed, n = self.parse_digit(tree, id)
            if (is_digit_parsed):
                parent_tree.paste(parent_node, tree)
                return True, n
        return False, n

    def parse_id(self, parent_tree, parent_node):
        """
        Defines production rule ID:
        ID -> WORD INTEGER | WORD 
        """
        if self.__is_parsed(): 
            return True, 0

        token = ""
        tree, id = self.__create_subtree(token,
                "id")
        is_word_parsed, n1 = self.parse_word(tree, id)
        is_integer_parsed, n2 = self.parse_integer(tree, id)

        if (is_word_parsed and is_integer_parsed):
            parent_tree.paste(parent_node, tree)
            return True, n1+n2 
        else:
            self.__rollback(n1+n2)
            tree, id = self.__create_subtree(token,
                    "id")
            is_word_parsed, n = self.parse_word(tree, id)
            if is_word_parsed:
                parent_tree.paste(parent_node, tree)
                return True, n
        return False, n

    def parse_exp(self, parent_tree, parent_node):
        """
        Defines production rule EXP:
        EXP -> ID OP ID
        """
        token = ""
        tree, id = self.__create_subtree(token,
                "exp")
        is_id_parsed, n1 = self.parse_id(tree, id)
        is_relation_parsed, n2 = self.parse_relation(tree, id)
        is_id_parsed, n3 = self.parse_id(tree, id)
        if is_id_parsed and is_relation_parsed and is_id_parsed:
            parent_tree.paste(parent_node, tree)
            return True, n1+n2+n3
        return False, n1+n2+n3

    def parse_kw_select(self, parent_tree, parent_node):
        """
        Defines production rule KW_SELECT:
        KW_SELECT -> S E L E C T WSS
        """
        kw_select = ''
        for i in range(6):
            kw_select += self.__next_token()
        if kw_select == 'select':
            tree, id = self.__create_subtree('select', "kw_select")
            parent_tree.paste(parent_node, tree)
            return True, 6
        return False, 6

    def parse_kw_where(self, parent_tree, parent_node):
        """
        Defines production rule KW_WHERE:
        KW_WHERE -> W H E R E
        """
        kw_where = ''
        for i in range(5):
            kw_where += self.__next_token()
        if kw_where == 'where':
            tree, id = self.__create_subtree('where', "kw_where")
            parent_tree.paste(parent_node, tree)
            return True, 5
        return False, 5

    def parse_kw_from(self, parent_tree, parent_node):
        """
        Defines production rule KW_FROM:
        KW_FROM -> F R O M
        """
        kw_from = ''
        for i in range(4):
            kw_from += self.__next_token()
        if kw_from == 'from':
            tree, id = self.__create_subtree('from', "kw_from")
            parent_tree.paste(parent_node, tree)
            return True, 4
        return False, 4

    def parse_select(self, parent_tree, parent_node):
        """
        Defines proudction rule SELECT:
        SELECT -> KW_SELECT ID KW_FROM ID KW_WHERE EXP
        """
        token = ""
        tree, id = self.__create_subtree(token,
                "select")
        is_kw_select_parsed, n1 = self.parse_kw_select(tree, id)
        is_id_parsed, n2 = self.parse_id(tree, id)
        is_kw_from_parsed, n3 = self.parse_kw_from(tree, id)
        is_id_parsed, n4 = self.parse_id(tree, id)
        is_kw_where_parsed, n5 = self.parse_kw_where(tree, id)
        is_exp_parsed, n6 = self.parse_exp(tree, id)
        if is_kw_select_parsed and \
           is_id_parsed and        \
           is_kw_from_parsed and   \
           is_id_parsed and        \
           is_kw_where_parsed and  \
           is_exp_parsed:
            parent_tree.paste(parent_node, tree)
            return True, n1+n2+n3+n4+n5+n6
        return False, n1+n2+n3+n4+n5+n6

    def parse(self, query):
        self.query = query
        #self.tokens = list(''.join(query.split()))
        self.tokens = list(query)
        self.current_position = 0
        self.parse_tree.create_node(query, 'root')
        self.parse_exp(self.parse_tree, 'root')  


    def print_parse_tree(self):
        print self.parse_tree.children('root')
        
        self.parse_tree.show()
        print "Current position is {}".format(self.current_position)


if __name__ == '__main__':
    
    parser = SQLParser()
    parser.parse('arse>=aarsen5213')
    #parser.parse('select name from students where age >= 15')
    parser.print_parse_tree()
    
