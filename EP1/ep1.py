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
        return "0"

    def actions(self, state):
        """ Metodo que implementa retorno da lista de acoes validas
        para um determinado estado
        """
        actions = []
        stateList = state.split()
        index = 0
        if len(stateList) > 0:
            index = int(stateList[-1])
        lastWord = self.query[index:]
        for i in range(1, len(lastWord) + 1):
            actions.append(lastWord[:i])
        # i = len(state)
        # while(state[i-1] != ' ' and i > 0):
        #     actions.append(str(i))
        #     i -= 1

        return actions

    def nextState(self, state, action):
        """ Metodo que implementa funcao de transicao """
        stateList = state.split()
        if len(stateList) > 0:
            newLast = int(stateList[-1]) + len(action)
        else:
            newLast = len(action)
        newState = state + " " + str(newLast)
        return newState

        # if int(action) == len(state):
        #     newState = state + ' '
        # else:
        #     newState = state[:int(action)] + ' ' + state[int(action):]

        return newState

    def isGoalState(self, state):
        """ Metodo que implementa teste de meta """
        stateList = state.split()
        if len(stateList) > 0 and int(stateList[-1]) == len(self.query):
            return True
        return False
        # stateList = state.split()
        # currentCost = self.unigramCost(stateList[-1])
        #
        # # Checa, com 3 graus de indireção, se ha alguma ação que diminuirá o
        # # valor total do estado. Em outras palavras, checa se alguma combinação
        # # de até 3 ações diminuirá o custo total do estado
        # for action in self.actions(state):
        #     newCost = self.stepCost(state, action)
        #     if newCost < currentCost:
        #         return False
        #
        # return True

    def stepCost(self, state, action):
        """ Metodo que implementa funcao custo """
        return self.unigramCost(action)
        # newState = self.nextState(state, int(action))
        # newStateList = newState.split()
        # if len(newStateList) <= 1:
        #     return self.unigramCost(newStateList[0])
        # if newState[-1] == ' ':
        #     return self.unigramCost(newStateList[-1])
        # return self.unigramCost(newStateList[-2])

def segmentWords(query, unigramCost):

    if len(query) == 0:
        return ''

    # BEGIN_YOUR_CODE
    # Voce pode usar a função getSolution para recuperar a sua solução
    # a partir do no meta
    problem = SegmentationProblem(query, unigramCost)
    goalNode = util.uniformCostSearch(problem)
    valid, solution  = util.getSolution(goalNode,problem)

    if valid:
        result = goalNode.state
        print(solution)
        return solution

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
        state = ' '.join(word for word in self.queryWords)
        return state

    def actions(self, state):
        """ Metodo  que implementa retorno da lista de acoes validas
        para um determinado estado
        """
        stateList = state.split()
        actions = []

        # Gera e devolve uma lista de tuplas, essas contendo
        # (indiçe da palavra no estado, palavra para a qual ela será substituida)
        for i in range(len(stateList)):
            word = stateList[i]
            for fill in self.possibleFills(self.queryWords[i]):
                if fill != word:
                    t = (i, fill)
                    actions.append(str(t))

        return actions

    def nextState(self, state, action):
        """ Metodo que implementa funcao de transicao """
        stateList = state.split()

        # Monta e devolve o novo estado baseado na ação action
        # index = action[0]
        # word = action[1]
        index, word = self.getAction(action)

        stateList[index] = word
        newState = ' '.join(word for word in stateList)

        return newState

    def isGoalState(self, state):
        """ Metodo que implementa teste de meta """
        currentCost = self.stateCost(state)
        stateList = state.split()

        # Aqui, checa que alguma das palavras do estado ainda são apenas
        # consoantes e possuem um possible fill
        for i in range(len(stateList)):
            if stateList[i] == self.queryWords[i]:
                if len(self.possibleFills(self.queryWords[i])) > 0:
                    return False

        # Checa se alguma ação abaixa o custo total do estado, com apenas
        # 1 grau de indireção
        for action1 in self.actions(state):
            newState1 = self.nextState(state, action1)
            newCost1 = self.stateCost(newState1)
            if newCost1 < currentCost:
                return False

        return True

    def stepCost(self, state, action):
        """ Metodo que implementa funcao custo """
        # Calcula o custo total do estado atual e do estado após realizar
        # a ação action, e devolve a diferença entre eles
        currentCost = self.stateCost(state)
        newState = self.nextState(state, action)
        newCost = self.stateCost(newState)

        return newCost - currentCost

    def stateCost(self, state):
        # Apenas calcula e devolve o valor total do estado dado
        stateList = state.split()
        cost = 0
        stateList.insert(0, util.SENTENCE_BEGIN)
        print(stateList)
        for i in range(len(stateList) - 1):
            cost += self.bigramCost(stateList[i], stateList[i+1])

        return cost

    def getAction(self, string):
        tmp = string.split()
        index = int(tmp[0][1:-1])
        word = tmp[1][1:-2]
        return (index, word)


def insertVowels(queryWords, bigramCost, possibleFills):
    # BEGIN_YOUR_CODE
    # Voce pode usar a função getSolution para recuperar a sua solução
    # a partir do no meta
    problem = VowelInsertionProblem(queryWords, bigramCost, possibleFills)
    goalNode = util.uniformCostSearch(problem)
    valid, solution  = util.getSolution(goalNode,problem)

    if valid:
        return goalNode.state
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
    ss = 'AccordingtoallknownlawsofaviationthereisnowaythatabeeshouldbeabletoflyItswingsaretoosmalltogetitsfatlittlebodyoffthegroundThebeeofcoursefliesanyways'
    str = "verydifficultstuff"
    # for i in range(len(str)):
    #     print(i, str[:i], str[i:])
    unigramCost, bigramCost, possibleFills  =  getRealCosts()
    print(bigramCost("sometimes", "later"))
    print(bigramCost("sometimes", "later"))
    print(bigramCost("ltr", "bcms"))
    print(bigramCost("later", "bcms"))
    print(bigramCost("later", "becomes"))

    # muito teste aaaaaaa
    # print(unigramCost(str))
    # for i in range(len(str)):
    #     str1 = str[:i]
    #     str2 = str[i:]
    #     print(str1, str2)
    #     print(unigramCost(str[:i]), unigramCost(str[i:]))
    #
    # print("sum", unigramCost("in"))
    # print(unigramCost("yourselfhavefaithinyourabilities"))
    # print("sum", unigramCost("in") + unigramCost("yourselfhavefaithinyourabilities"))
    # print("sum", unigramCost("very") + unigramCost("difficult"))
    # print("sum", unigramCost("verydif") + unigramCost("ficult"))
    #
    # print(2, unigramCost("v"))
    # print(3, unigramCost("ve"))
    # print(4, unigramCost("ver"))
    # print(5, unigramCost("very"))
    # print(6, unigramCost("veryd"))
    # print('b', bigramCost("very", "difficult"))

    print("be: ",unigramCost("be"))
    print(unigramCost("lieveinyourself"))

    resulSegment = segmentWords(s, unigramCost)
    print("resultado: ",resulSegment)

    # resulSegment = segmentWords("imagineallthepeople", unigramCost)
    # print("resultado2: ",resulSegment)

    # resultInsert = insertVowels('smtms ltr bcms nvr'.split(), bigramCost, possibleFills)
    # print("resultado: ", resultInsert)

if __name__ == '__main__':
    main()
