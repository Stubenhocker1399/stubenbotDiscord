import discord
from discord.ext import commands
#import asyncio
##
import ast
from collections import deque
import contextlib
import sys
#import StringIO 
from io import StringIO
##

#client = discord.Client()
description = '''A discord.py test
'''
bot = commands.Bot(command_prefix='/', description=description)

####################


@contextlib.contextmanager
def stdoutIO(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old

def safe_call(*args, **kwargs):
    #print "safe_call() with args: "
    #for arg in args:
    #	print str(arg)
    #return None 
    g_functionWhitelist = [str, len, range, abs, dict, min, max, all, any, bin, bool, bytearray, bytes, chr, complex, setattr, delattr, divmod, enumerate, filter, float, format, frozenset, hasattr, hash, hex, id, int, isinstance, issubclass, iter, list, next, object, oct, ord, pow, repr, reversed, round, set, slice, sorted, staticmethod, str, sum, super, tuple, type, zip, str, print]

    func = args[0]
    argumentList = list(args)
    #print "trying to call function: " + func.__name__
    for f in g_functionWhitelist:
        if func == f:
            argumentList.pop(0)	# pop the actual function that we call
            return f(*argumentList, **kwargs)
    print("trying to call forbidden function: " + func.__name__)
    return None
    


class FuncCallVisitor(ast.NodeVisitor):
    def __init__(self):
        self._name = deque()

    @property
    def name(self):
        return '.'.join(self._name)

    @name.deleter
    def name(self):
        self._name.clear()

    def visit_Name(self, node):
        self._name.appendleft(node.id)

    def visit_Attribute(self, node):
        try:
            self._name.appendleft(node.attr)
            self._name.appendleft(node.value.id)
        except AttributeError:
            self.generic_visit(node)

class FuncCallRemover(ast.NodeTransformer):
    def visit_Call(self, node):
        callvisitor = FuncCallVisitor()
        callvisitor.visit(node.func)
        return ast.Call(func=ast.Name(id="safe_call", ctx=ast.Load(), lineno=0, col_offset=0), args=([node.func] + node.args), keywords=node.keywords, lineno=0, col_offset=0) 

def get_func_calls(tree):
    func_calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            callvisitor = FuncCallVisitor()
            callvisitor.visit(node.func)
            func_calls.append(callvisitor.name)

    return func_calls

def resolve_object(name):
    names = name.split('.')
    return reduce(getattr, names[1:], globals()[names[0]])

class FuncDeclVisitor(ast.NodeVisitor):
    def __init__(self):
        self._decls = list()
    def visit_FunctionDef(self, node):
        self._decls.append(node.name)
@bot.command()
#async def py(code : str):
async def py(ctx, *, code):
    print(">>>>>>>>>")
    print(code)
    print("<<<<<<<<<")
    if (code=="help"):
        await bot.say("""`Usage:`
/py \`\`\`py
<your code here>
\`\`\`
        """)
    statement = code
    print("###########")
    print(code)
    print("###########")
    if(statement[:6]==" ```py"):
        statement = code[6:]
    if(statement[-3:]=="```"):
        statement = code[:-3]
    print("ECHO: " + statement)
    print("###########")
    module = None
    try: 
        module = ast.parse(statement)
    except Exception as e:
        module = None
        print("parse error: " + str(e))
        await bot.say("```\n"+"parse error: " + str(e)+"```")
    if module != None:
        declCollector = FuncDeclVisitor()
        declCollector.visit(module)
        for decl in declCollector._decls:
            print("found func decl: " + str(decl))
            await bot.say("```\n"+"found func decl: " + str(decl)+"```")
            #func = resolve_object(str(decl))
            #if func is not None:
            #	print "added to whitelist: " + str(func)
            #	await bot.say("```\n"+"added to whitelist: " + str(func)+"```")
            #	global g_functionWhitelist
            #	g_functionWhitelist.append(func)

        print(get_func_calls(module))
        FuncCallRemover().visit(module)
        compileResult = None
        try:
            compileResult = compile(module, '<string>', 'exec')
        except Exception(e):
            compileResult = None
            print("compilation error: " + str(e))
            await bot.say("```\n"+"compilation error: " + str(e)+"```")
        if compileResult != None:
            with stdoutIO() as s:
                try:
                    exec(compileResult)
                except Exception(e):
                    print("runtime error: " + str(e))
                    #await bot.say("```\n"+"runtime error: " + str(e)+"```")
                if not s.getvalue() == "":
                    #await bot.say(s.getvalue())
                    await bot.say("```\n"+s.getvalue()+"```")


####################


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

#@client.event
#async def on_message(message):
#    if message.content.startswith('!test'):
#        counter = 0
#        tmp = await client.send_message(message.channel, 'Calculating messages...')
#        async for log in client.logs_from(message.channel, limit=100):
#            if log.author == message.author:
#                counter += 1
#
#        await client.edit_message(tmp, 'You have {} messages.'.format(counter))
#
#//@bot.command()
#//async def testcmd(ctx,inputstr : str):
#//    """Just a test."""
#//    await ctx.say(inputstr)

#@bot.command()
#async def hello(ctx):
#    await ctx.say("world")
@bot.command()
async def hello():
    """Say world."""
    await bot.say("world")

with open("token") as token:
    bot.run(token.read())