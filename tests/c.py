"""
Copyright, 2010, Paul McGuire
Script: c.py
Description: A subset-C parser (BNF taken from the 1996 International Obfuscated C Code Contest)
             https://www.ioccc.org/1996/august.hint

OC Grammar
==========
Terminals are in quotes, () is used for bracketing.

program:
    decl*

decl:
    vardecl
    fundecl

vardecl:
    type NAME ;
    type NAME "[" INT "]" ;

fundecl:
    type NAME "(" args ")" "{" body "}"

args:
    /*empty*/
    ( arg "," )* arg

arg:
    type NAME

body:
    vardecl* stmt*

stmt:
    ifstmt
    whilestmt
    dowhilestmt
    "return" expr ";"
    expr ";"
    "{" stmt* "}"
    ";"

ifstmt:
    "if" "(" expr ")" stmt
    "if" "(" expr ")" stmt "else" stmt

whilestmt:
    "while" "(" expr ")" stmt

dowhilestmt:
    "do" stmt "while" "(" expr ")" ";"

expr:
    expr binop expr
    unop expr
    expr "[" expr "]"
    "(" expr ")"
    expr "(" exprs ")"
    NAME
    INT
    CHAR
    STRING

exprs:
    /*empty*/
    (expr ",")* expr

binop:
    "+" | "-" | "*" | "/" | "%" |
    "=" |
    "<" | "==" | "!="

unop:
    "!" | "-" | "*"

type:
    "int" stars
    "char" stars

stars:
    "*"*
"""

import pyparsing as pp

pp.ParserElement.enablePackrat()

LPAR, RPAR, LBRACK, RBRACK, LBRACE, RBRACE, SEMI, COMMA = map(pp.Suppress, "()[]{};,")
INT, CHAR, WHILE, DO, IF, ELSE, RETURN = map(pp.Keyword, "int char while do if else return".split())

NAME = pp.Word(pp.alphas + "_", pp.alphanums + "_")
integer = pp.Regex(r"[+-]?\d+")
char = pp.Regex(r"'.'")
string_ = pp.dbl_quoted_string

TYPE = pp.Group((INT | CHAR) + pp.ZeroOrMore("*"))
expr = pp.Forward()
func_call = pp.Group(NAME + LPAR + pp.Group(pp.Optional(pp.DelimitedList(expr))) + RPAR)
operand = func_call | NAME | integer | char | string_
expr <<= pp.infix_notation(
    operand,
    [
        (pp.one_of("! - *"), 1, pp.opAssoc.RIGHT),
        (pp.one_of("++ --"), 1, pp.opAssoc.RIGHT),
        (pp.one_of("++ --"), 1, pp.opAssoc.LEFT),
        (pp.one_of("* / %"), 2, pp.opAssoc.LEFT),
        (pp.one_of("+ -"), 2, pp.opAssoc.LEFT),
        (pp.one_of("< == > <= >= !="), 2, pp.opAssoc.LEFT),
        (pp.Regex(r"(?<!=)=(?!=)"), 2, pp.opAssoc.LEFT),
    ],
) + pp.Optional(
    LBRACK + expr + RBRACK | LPAR + pp.Group(pp.Optional(pp.DelimitedList(expr))) + RPAR
)

stmt = pp.Forward()

ifstmt = IF - LPAR + expr + RPAR + stmt + pp.Optional(ELSE + stmt)
whilestmt = WHILE - LPAR + expr + RPAR + stmt
dowhilestmt = DO - stmt + WHILE + LPAR + expr + RPAR + SEMI
returnstmt = RETURN - expr + SEMI

stmt << pp.Group(
    ifstmt
    | whilestmt
    | dowhilestmt
    | returnstmt
    | expr + SEMI
    | LBRACE + pp.ZeroOrMore(stmt) + RBRACE
    | SEMI
)

vardecl = pp.Group(TYPE + NAME + pp.Optional(LBRACK + integer + RBRACK)) + SEMI

arg = pp.Group(TYPE + NAME)
body = pp.ZeroOrMore(vardecl) + pp.ZeroOrMore(stmt)
fundecl = pp.Group(
    TYPE
    + NAME
    + LPAR
    + pp.Optional(pp.Group(pp.DelimitedList(arg)))
    + RPAR
    + LBRACE
    + pp.Group(body)
    + RBRACE
)
decl = fundecl | vardecl
program = pp.ZeroOrMore(decl)

program.ignore(pp.c_style_comment)

# set parser element names
for vname in (
    "ifstmt whilestmt dowhilestmt returnstmt TYPE "
    "NAME fundecl vardecl program arg body stmt".split()
):
    v = vars()[vname]
    v.setName(vname)

# ~ for vname in "fundecl stmt".split():
# ~ v = vars()[vname]
# ~ v.setDebug()


def main():
    test = r"""
    /* A factorial program */
    int
    putstr(char *s)
    {
        while(*s)
            putchar(*s++);
    }
    
    int
    fac(int n)
    {
        if (n == 0)
            return 1;
        else
            return n*fac(n-1);
    }
    
    int
    putn(int n)
    {
        if (9 < n)
            putn(n / 10);
        putchar((n%10) + '0');
    }
    
    int
    facpr(int n)
    {
        putstr("factorial ");
        putn(n);
        putstr(" = ");
        putn(fac(n));
        putstr("\n");
    }
    
    int
    main()
    {
        int i;
        i = 0;
        if(a() == 1){}
        while(i < 10)
            facpr(i++);
        return 0;
    }
    """

    ast = program.parse_string(test, parseAll=True)
    ast.pprint()


if __name__ == "__main__":
    main()
