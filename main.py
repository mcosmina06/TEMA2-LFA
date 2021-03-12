import sys

class AF:
    def __init__(self, NumberOfStates, StartState, FinaleStates, TransitionTable, Alfabet):
        self.NumberOfStates = NumberOfStates
        self.StartState = StartState
        self.FinaleStates = FinaleStates
        self.TransitionTable = TransitionTable
        self.Alfabet = Alfabet

def read_input(filename):
    InputFile = open(filename, "r")
    data = InputFile.readlines()
    InputFile.close()
    alfabet = []

    #numarul de stari
    NumberOfStates = int(data[0])
    #print(NumberOfStates)
   
    #lista starilor finale
    FinaleStates = []
    for i in data[1].split(" "):
        FinaleStates.append(int(i))
    #print(FinaleStates)
    
    #matricea de tranzitii de forma TransitionTable{0:{a:0, b:2}, 1:{a:2}}
    TransitionTable = {}
    for i in range(0, NumberOfStates):
        TransitionTable[i] = {}
    
    for i in data[2:]:
        line = i.split(" ")
        TransitionTable[int(line[0])][line[1]] = []
        for j in line[2:]:
        	TransitionTable[int(line[0])][line[1]].append(int(j))
        	if line[1] not in alfabet:
        		alfabet.append(line[1])
    alfabet.sort()
    return AF(NumberOfStates, 0, FinaleStates, TransitionTable, alfabet)

#functia returneaza multimea de stari in care putem ajunge
#dintr-o multime de stari data si un caracter
def compute_SetOfTans_from_SetOfTans(TransitionTable, M1, c): 
	M2 = set()

	for i in M1:
		if c in TransitionTable[i].keys():
			for i in TransitionTable[i][c]:
				M2.add(i)
	return M2

# generez multimea de epsilon inchidere ce este reprezentata
# printr - o lista de seturi corespunzatoare fiecarei stari
# a NFA ului
def compute_EpsilonClosure(TransitionTable):
	n = len(TransitionTable.keys())
	
	#multimea finala de epsilon inciderei pentru fiecare stare
	MofEpsilons = [set() for i in range(n)]
	
	# pentru fiecare stare din tabel generez noua stare pe care pot ajunge pe epsilon
	for i in (TransitionTable.keys()):
		MofEpsilons[i] = set()
		MofEpsilons[i] = compute_SetOfTans_from_SetOfTans(TransitionTable, [i], 'eps')
		MofEpsilons[i].add(i)
	
	# trebuiesc pentru fiecare stare adaugate si celelte tranzitii
	# "indirecte" de epsilon
	ok = 0
	while ok == 0:                                              
		ok = 1                                                  
		for i in range(n):
			ex = MofEpsilons[i]
			# fac reuniunea dintre epsilon-inchiderea fiecarei stari deja existente
			# cu multimea curenta pana cand nu se mai semnaleaza modificari
			for j in MofEpsilons[i]:
				MofEpsilons[i] = MofEpsilons[i] | MofEpsilons[j]
				if ex != MofEpsilons[i]:
					ok = 0
	return MofEpsilons

# generez a doua matrice de tranzitii de formma unui dictionar de
# dictionare, asemeni primei tabele.
def compute_TransitionTable2(NFA):
	n = len(NFA.Alfabet)
	m = NFA.NumberOfStates

	# calculez inchiderile epsilon pentru fiecare stare a NFA-ului
	EpsilonClosure = compute_EpsilonClosure(NFA.TransitionTable)
	
	# noua matrice de tranzitii
	TransitionTable2 = {}
	
	# initial adaug in "coada" inchiderea epsilon a starii initiale, 0
	queue = [EpsilonClosure[0]]
	for state in queue:
		# adaug intrare specifica starii pe care ma aflu in dictionare
		TransitionTable2[queue.index(state)] = {}
		# si pentru fiecare caracter, mai putin epsilon completez cu 
		# noua stare in care pot ajunge
		for i in NFA.Alfabet:
			if i == 'eps':
				continue
			# ma folosesc de functia scrisa mai sus pentru a aflarea noua stare
			# in care ma duce stare curent pe carcaterul i din alfabet
			aux = compute_SetOfTans_from_SetOfTans(NFA.TransitionTable, state, i)
			# fac reuniunea dintre epsilon inchiderile fiecarei stari din multimea
			# de stari obtinute
			new_state = aux
			for j in aux:
				new_state = new_state | EpsilonClosure[j]
			# completez tabelul
			TransitionTable2[queue.index(state)][i] = new_state
			# si daca nu este prezenta in coada o adaug
			if new_state not in queue:
				queue.append(new_state)
	
	# marchez starile finale, adaug in lista DFA-ului doar acele
	# stari ce contin starea finala a NFA-ului
	NewFinalStates = []
	for i in queue:
		for k in NFA.FinaleStates:
			if k in i:
				if queue.index(i) not in NewFinalStates:
					NewFinalStates.append(queue.index(i))

	# codific starile de tabel in functie de indexul lor din coada
	for i in TransitionTable2.keys():
		for j in TransitionTable2[i]:
			TransitionTable2[i][j] = queue.index(TransitionTable2[i][j])

	#numarul de stari finale ale DFA-ului
	NumberOfStates = len(TransitionTable2.keys())
	
	#am adaugat sink state ul si tranzitiile pe el
	TransitionTable2[NumberOfStates] = {}
	for i in NFA.Alfabet:
		if i == 'eps':
			continue
		TransitionTable2[NumberOfStates][i] = NumberOfStates

	# verific daca exista tranzitii de adaugat de la celelalte stari
	for i in TransitionTable2.keys():
		for k in NFA.Alfabet:
			if k == 'eps':
				continue
			if k not in TransitionTable2[i].keys():
				TransitionTable2[i][k] = NumberOfStates

	return AF(NumberOfStates, 0, NewFinalStates, TransitionTable2, NFA.Alfabet)

# scrierea outputului in fisier
def write_output(filename, DFA):
	OutputFile = open(filename, "w")

	OutputFile.write(str(DFA.NumberOfStates))
	OutputFile.write(str("\n"))
	
	for i in DFA.FinaleStates:
		OutputFile.write(str(i))
		if i != DFA.FinaleStates[len(DFA.FinaleStates) - 1]:
			OutputFile.write(str(" "))
	OutputFile.write(str("\n"))

	for i in DFA.TransitionTable.keys():
		for j in DFA.TransitionTable[i]:
			OutputFile.write(str(i) + str(" ") + str(j) + str(" ") + str(DFA.TransitionTable[i][j]))
			OutputFile.write(str("\n"))

	OutputFile.close()

if __name__ == '__main__':
	NFA = read_input(str(sys.argv[1]))
	DFA = compute_TransitionTable2(NFA)
	write_output(str(sys.argv[2]), DFA)
	