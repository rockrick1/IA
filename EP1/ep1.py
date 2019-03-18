"""
  AO PREENCHER ESSE CABECALHO COM O MEU NOME E O MEU NUMERO USP,
  DECLARO QUE SOU A UNICA PESSOA AUTORA E RESPONSAVEL POR ESSE PROGRAMA.
  TODAS AS PARTES ORIGINAIS DESSE EXERCICIO PROGRAMA (EP) FORAM
  DESENVOLVIDAS E IMPLEMENTADAS POR MIM SEGUINDO AS INSTRUCOES
  DESSE EP E, PORTANTO, NAO CONSTITUEM ATO DE DESONESTIDADE ACADEMICA,
  FALTA DE ETICA OU PLAGIO.
  DECLARO TAMBEM QUE SOU A PESSOA RESPONSAVEL POR TODAS AS COPIAS
  DESSE PROGRAMA E QUE NAO DISTRIBUI OU FACILITEI A
  SUA DISTRIBUICAO. ESTOU CIENTE QUE OS CASOS DE PLAGIO E
  DESONESTIDADE ACADEMICA SERAO TRATADOS SEGUNDO OS CRITERIOS
  DIVULGADOS NA PAGINA DA DISCIPLINA.
  ENTENDO QUE EPS SEM ASSINATURA NAO SERAO CORRIGIDOS E,
  AINDA ASSIM, PODERAO SER PUNIDOS POR DESONESTIDADE ACADEMICA.

  Nome : Henrique Cerquinho
  NUSP : 9793700

  Referencias: Com excecao das rotinas fornecidas no enunciado
  e em sala de aula, caso voce tenha utilizado alguma referencia,
  liste-as abaixo para que o seu programa nao seja considerado
  plagio ou irregular.

  Exemplo:
  - O algoritmo Quicksort foi baseado em:
  https://pt.wikipedia.org/wiki/Quicksort
  http://www.ime.usp.br/~pf/algoritmos/aulas/quick.html
"""

import util

############################################################
# Part 1: Segmentation problem under a unigram model

class SegmentationProblem(util.Problem):
    def __init__(self, query, unigramCost):
        self.query = query
        self.unigramCost = unigramCost

    def isState(self, state):
        """ Metodo que implementa verificacao de estado """
        if self.state == state:
            return True
        return False

    def initialState(self):
        """ Metodo que implementa retorno da posicao inicial """
        state = self.query
        # numsei
        return state

    def actions(self, state):
        """ Metodo que implementa retorno da lista de acoes validas
        para um determinado estado
        """
        stateList = state.split()
        last = stateList[-1]
        best = self.unigramCost(last)
        actions = []
        for i in range(1, len(last)):
            split1 = last[:i]
            split2 = last[i:]
            cost = self.unigramCost(split1) + self.unigramCost(split2)
            if cost < best:
                actions = []
                best = cost
                actions.append(str(i))
            elif cost == best:
                actions.append(str(i))
        print(actions)
        return actions

    def nextState(self, state, action):
        """ Metodo que implementa funcao de transicao """
        stateList = state.split()
        last = stateList.pop()
        str1 = last[:int(action)]
        str2 = last[int(action):]

        stateList.append(str1)
        stateList.append(str2)
        newState = ' '.join(word for word in stateList)
        return newState

    def isGoalState(self, state):
        """ Metodo que implementa teste de meta """
        stateList = state.split()
        last = stateList[-1]
        cost = self.unigramCost(last)
        for i in range(len(last)):
            splitCost = self.unigramCost(last[:i]) + self.unigramCost(last[i:])
            if splitCost < cost:
                return False
        print("é, cabou")
        return True

    def stepCost(self, state, action):
        """ Metodo que implementa funcao custo """
        stateList = state.split()
        now = self.unigramCost(stateList[-1])
        next = self.unigramCost(stateList[-1][int(action):])
        return now - next

def segmentWords(query, unigramCost):

    if len(query) == 0:
        return ''

    # BEGIN_YOUR_CODE
    # Voce pode usar a função getSolution para recuperar a sua solução
    # a partir do no meta
    problem = SegmentationProblem(query, unigramCost)
    goalNode = util.uniformCostSearch(problem)
    print("goal: ", goalNode.state)
    valid,solution  = util.getSolution(goalNode,problem)

    if valid:
        return solution
    else:
        print("fudeu mermao")

    # END_YOUR_CODE

############################################################
# Part 2: Vowel insertion problem under a bigram cost

class VowelInsertionProblem(util.Problem):
    def __init__(self, queryWords, bigramCost, possibleFills):
        self.queryWords = queryWords
        self.bigramCost = bigramCost
        self.possibleFills = possibleFills

    def isState(self, state):
        if self.state == state:
            return True
        return False

    def initialState(self):
        """ Metodo  que implementa retorno da posicao inicial """
        raise NotImplementedError

    def actions(self, state):
        """ Metodo  que implementa retorno da lista de acoes validas
        para um determinado estado
        """
        raise NotImplementedError

    def nextState(self, state, action):
        """ Metodo que implementa funcao de transicao """
        raise NotImplementedError

    def isGoalState(self, state):
        """ Metodo que implementa teste de meta """
        raise NotImplementedError

    def stepCost(self, state, action):
        """ Metodo que implementa funcao custo """
        raise NotImplementedError



def insertVowels(queryWords, bigramCost, possibleFills):
    # BEGIN_YOUR_CODE
    # Voce pode usar a função getSolution para recuperar a sua solução
    # a partir do no meta
    # valid,solution  = util.getSolution(goalNode,problem)
    raise NotImplementedError
    # END_YOUR_CODE

############################################################


def getRealCosts(corpus='corpus.txt'):

    """ Retorna as funcoes de custo unigrama, bigrama e possiveis fills
    obtidas a partir do corpus.
    """

    _realUnigramCost, _realBigramCost, _possibleFills = None, None, None
    if _realUnigramCost is None:
        print('Training language cost functions [corpus: '+ corpus+']... ')

        _realUnigramCost, _realBigramCost = util.makeLanguageModels(corpus)
        _possibleFills = util.makeInverseRemovalDictionary(corpus, 'aeiou')

        print('Done!')

    return _realUnigramCost, _realBigramCost, _possibleFills

def main():
    """ Voce pode/deve editar o main() para testar melhor sua implementacao.

    A titulo de exemplo, incluimos apenas algumas chamadas simples para
    lhe dar uma ideia de como instanciar e chamar suas funcoes.
    Descomente as linhas que julgar conveniente ou crie seus proprios testes.
    """
    s = 'believeinyourselfhavefaithinyourabilities'
    str = "verydifficult"
    for i in range(len(str)):
        print(i, str[:i], str[i:])
    unigramCost, bigramCost, possibleFills  =  getRealCosts()

    print(unigramCost(""))
    ss = "inyourselfhavefaithinyourabilities"
    for i in range(len(ss)):
        if unigramCost(ss[:i]) + unigramCost(ss[i:]) < unigramCost(ss):
            print("tem melhor", i)

    print("sum", unigramCost("in") + unigramCost("yourselfhavefaithinyourabilities"))
    print("sum", unigramCost("very") + unigramCost("difficult"))
    print("sum", unigramCost("verydif") + unigramCost("ficult"))

    print(2, unigramCost("v"))
    print(3, unigramCost("ve"))
    print(4, unigramCost("ver"))
    print(5, unigramCost("very"))
    print(6, unigramCost("veryd"))
    print('b', bigramCost("very", "difficult"))

    resulSegment = segmentWords(s, unigramCost)
    print("resultado: ",resulSegment)


    # resultInsert = insertVowels('smtms ltr bcms nvr'.split(), bigramCost, possibleFills)
    # print(resultInsert)

if __name__ == '__main__':
    main()
