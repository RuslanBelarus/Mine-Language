from typing import Any, Callable
from shutil import rmtree
from sys import argv
from os import mkdir

#комманда для запуска:
#python main.py scripts\script.mc C:\Users\admin\AppData\Roaming\.minecraft\saves\Script

TOKENS = [
    ['fn', '<fn>'],
    ['end', '<end>'],
    ['execute', '<ex>'],
]

class ModsHandler:
    LocalAnoncement = [lambda values, tokens_line, extokens: extokens]
    TranslatedFunctions = [lambda tokens_line, excode, values: excode]

class ModLoader:

    def Att(fromTokens, toTokens):
        for token_set in fromTokens:
            key, item = token_set[0], token_set[1]
            toTokens.append([key, item])

    def ModLoader(path):
        modName = path.split('/')[len(path.split('/'))-1].replace('.mh', '')

        exec(open(path, 'r', encoding='utf-8').read())
        
        exec(f'ModsHandler.LocalAnoncement.append({modName}.LocalAnoncement)')
        exec(f'ModsHandler.TranslatedFunctions.append({modName}.TranslatedFunctions)')
        exec(f'ModLoader.Att({modName}.LocTokens, TOKENS)')

        print(f'{modName} mod loading sucsessfull')
    
    def Pack(code):
        xcode = str()

        for line in code.split('\n'):
            _line = line.split(' ')

            if _line[0] == 'pack':
                ModLoader.ModLoader(_line[1])
            
            else:
                xcode += line
            
            xcode += '\n'
        
        print()
        
        return xcode

class workspace:

    SOURCE_LOAD_CODE = {
        'pack.mcmeta':'{"pack": {"pack_format": 12,"description": "Generated sript"}}',
        'tick.json':'{"values": ["script:main"]}',
        'load.json':'{"values": ["script:setup"]}'
    }
    
    def Write(world_path,toFunc):
        '''Функция разносит и создает функции и в функции заптисывет код им надлежащий'''

        loc = f'{world_path}/datapacks/script/data/script/functions/$.mcfunction'
        fnames = list(toFunc.keys())
        for name in fnames:
            with open(loc.replace('$', name), 'w', encoding='utf-8') as f:
                f.write(toFunc[name])

    def Create(world_path):
        '''Функция создает окружение ввиде основы для датапака для использования и ззагрузки конвертированного кода'''

        try: rmtree(world_path+"/script")
        except: pass

        crlog = [
            'script',
            'script/pack.mcmeta',
            'script/data',
            'script/data/minecraft',
            'script/data/minecraft/tags',
            'script/data/minecraft/tags/functions',
            'script/data/minecraft/tags/functions/load.json',
            'script/data/minecraft/tags/functions/tick.json',
            'script/data/script',
            'script/data/script/functions',
            'script/data/script/functions/main.mcfunction',
            'script/data/script/functions/setup.mcfunction'
        ]

        for path in crlog:

            _path = f'{world_path}/{path}'
            
            print(_path)

            if _path.split('/')[len(_path.split('/'))-1].find('.') == -1:
                try:
                    mkdir(_path)
                except:
                    pass

            else:
                with open(_path, 'w', encoding='utf-8') as f:
                    fname = _path.split('/')[len(_path.split('/'))-1]
                    try:
                        f.write(workspace.SOURCE_LOAD_CODE[fname])
                    except:
                        f.write(' ')

class locwork:
    
    def getTokenValues(token):
        '''Функция для получчения имени и значения токена'''

        length = len(token.split('='))
        if length == 1:
            name = token.split('=')[0].replace('<','').replace('>','')
            value = None
        else:
            name = token.split('=')[0].replace('<','')
            value = token.split('=')[1].replace('>','')
        return (name, value)
    
    def verifTokenQueue(tokens_line, *args):
        '''Функция создана для проверки надлежащего расположения очереди токенов'''

        for i, token in enumerate(tokens_line):
            name, _ = locwork.getTokenValues(token)

            if name == args[i]:
                pass
            else:
                return False

        else:
            return True

class Lexer:

    def _TypeDefine(word):
        '''Локальная функция служущая для определения вне списковых значений'''

        try:
            token = f'<int={int(word)}>'
        except:
            token = f'<word={str(word)}>'
        if word[0] + word[len(word)-1] == '""':
            token = f'<string={str(word).replace('"', '')}>'

        return token

    def Parse(xcode):
        '''Функция для разделения кода на строки токенов'''

        tokens = list()

        for ln in xcode.split('\n'):
            if ln == '': continue

            local_tokens = list()
            
            for word in ln.split(' '):
                for token in TOKENS:
                    if token[0] == word:
                        local_tokens.append(token[1])
                        break
                else:
                    local_tokens.append( Lexer._TypeDefine(word) )
            
            tokens.append( local_tokens )
        
        return tokens

class Ruler:

    replacable_list: list = [
        ['\n\n', '\n']
    ]
    
    def Processing(code):
        '''Функция для проверки и устранения исключений'''

        for rule in Ruler.replacable_list:
            while code.find(rule[0]) > 0:
                code = code.replace(rule[0], rule[1])
        return code
    
    def TakeError(note, condition = True):
        if condition: raise BaseException(note)

class Export:

    def Loc(tokens):
        '''Функция для локальной работы с компиоируемыми данными, таких как создание и именение значений перемнных'''

        extokens = list()
        values = dict()

        for tokens_line in tokens:

            for mod in ModsHandler.LocalAnoncement: extokens = mod(values, tokens_line, extokens)

        return values, extokens

    def Ex(values, tokens):
        '''Функция для конвертации цепи токенов в .mcfunction комманд'''

        excode = str()

        for tokens_line in tokens:

            for mod in ModsHandler.TranslatedFunctions : excode = mod(tokens_line, excode, values)

            if locwork.verifTokenQueue(tokens_line, 'fn', 'word'):
                _, value = locwork.getTokenValues(tokens_line[1])
                excode += f'fn {value}'
            
            elif locwork.verifTokenQueue(tokens_line, 'end'):
                excode += f'end'
            
            elif locwork.verifTokenQueue(tokens_line, 'ex', 'word'):
                _, value = locwork.getTokenValues(tokens_line[1])
                excode += f'function script:{value}'

            excode += '\n'

        return excode
    
    def Distributor(excode):
        '''Функция служущая разделителем строк кода по функциям, ими надлещими'''

        toFunc = {}
        
        fn_open = False
        fn_name = str()

        for line in excode.split('\n'):

            if line == 'end':
                fn_open = False
                fn_name = str()
            
            if fn_open:
                toFunc[fn_name] += line + '\n'

            if line.split(' ')[0] == 'fn':
                fn_open = True
                fn_name = line.split(' ')[1]
                toFunc[fn_name] = ''
        
        return toFunc

def main():
    path, world = argv[1], argv[2]
    if path.find('.mc') < 0: Ruler.TakeError("Name type not current.")

    print(' work in', world, '\n', 'code in', path, '\n')

    code: AbstractCode = open(path, 'r', encoding='utf-8').read()
    code: AbstractCode = Ruler.Processing(code)
    xcode: AbstractCode = ModLoader.Pack(code)
    tokens: AbstractToken = Lexer.Parse(xcode)
    values, extokens = Export.Loc(tokens)
    excode: AbstractCode = Export.Ex(values, extokens)
    toFunc: AbstractSets = Export.Distributor(excode)
    workspace.Create(world+'/datapacks')
    workspace.Write(world,toFunc)

    print(f'\nlocal values: {values}\n\nWork sucsessfull')

if __name__ == '__main__':
    type AbstractCode = Callable[[None], str]
    type AbstractToken = Callable[[None], list[str]]
    type AbstractValue = Callable[[None], dict[str]]
    type AbstractSets = Callable[[None], dict[AbstractCode]]

    main()