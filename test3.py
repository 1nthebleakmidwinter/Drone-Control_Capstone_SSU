import sys
import copy
sys.setrecursionlimit(10000)

NandM = sys.stdin.readline().rstrip().split(' ')
N = int(NandM[0])
M = int(NandM[1])

board = []
R_visited = []
B_visited = []
for n in range(N) :
    temp = []
    temp2 = []
    info = sys.stdin.readline().rstrip()

    for m in range(M) :
        if info[m] == 'R' :
            Ry = n
            Rx = m
        elif info[m] == 'B' :
            By = n
            Bx = m
        elif info[m] == 'O' :
            Oy = n
            Ox = m
        temp.append(info[m])
    board.append(temp)

    for m in range(M) :
        temp2.append(True)
    R_visited.append(temp2)
    B_visited.append(temp2)

def around_marble(process, Rxy) :
    up = process[Rxy[0]-1][Rxy[1]]
    down = process[Rxy[0]+1][Rxy[1]]
    left = process[Rxy[0]][Rxy[1]-1]
    right = process[Rxy[0]][Rxy[1]+1]

    return [up, down, left, right]

def tilting(process, Rxy, Bxy, Oxy, rsv) :
    R_fall = False
    B_fall = False
    if rsv == 0 :
        if Bxy[0] == Oxy[0] and Bxy[1] == Oxy[1] :
            B_fall = True
        elif process[Bxy[0]-1][Bxy[1]] == '.' :
            process[Bxy[0]-1][Bxy[1]] = 'B'
            process[Bxy[0]][Bxy[1]] = '.'
            Bxy[0] -= 1
        elif process[Bxy[0]-1][Bxy[1]] == 'O' :
            process[Bxy[0]][Bxy[1]] = '.'
            Bxy[0] -= 1
        
        if Rxy[0] == Oxy[0] and Rxy[1] == Oxy[1] :
            R_fall = True
        elif process[Rxy[0]-1][Rxy[1]] == '.' :
            process[Rxy[0]-1][Rxy[1]] = 'R'
            process[Rxy[0]][Rxy[1]] = '.'
            Rxy[0] -= 1
        elif process[Rxy[0]-1][Rxy[1]] == 'O' :
            process[Rxy[0]][Rxy[1]] = '.'
            Rxy[0] -= 1
            
        if (R_fall or process[Rxy[0]-1][Rxy[1]] == '#' or process[Rxy[0]-1][Rxy[1]] == 'B') and (B_fall or process[Bxy[0]-1][Bxy[1]] == '#' or process[Bxy[0]-1][Bxy[1]] == 'R') :
            return
        
    elif rsv == 1 :
        if Bxy[0] == Oxy[0] and Bxy[1] == Oxy[1] :
            B_fall = True
        elif process[Bxy[0]+1][Bxy[1]] == '.' :
            process[Bxy[0]+1][Bxy[1]] = 'B'
            process[Bxy[0]][Bxy[1]] = '.'
            Bxy[0] += 1
        elif process[Bxy[0]+1][Bxy[1]] == 'O' :
            process[Bxy[0]][Bxy[1]] = '.'
            Bxy[0] += 1

        if Rxy[0] == Oxy[0] and Rxy[1] == Oxy[1] :
            R_fall = True
        elif process[Rxy[0]+1][Rxy[1]] == '.' :
            process[Rxy[0]+1][Rxy[1]] = 'R'
            process[Rxy[0]][Rxy[1]] = '.'
            Rxy[0] += 1
        elif process[Rxy[0]+1][Rxy[1]] == 'O' :
            process[Rxy[0]][Rxy[1]] = '.'
            Rxy[0] += 1
            
        if (R_fall or process[Rxy[0]+1][Rxy[1]] == '#' or process[Rxy[0]+1][Rxy[1]] == 'B') and (B_fall or process[Bxy[0]+1][Bxy[1]] == '#' or process[Bxy[0]+1][Bxy[1]] == 'R') :
            return
        
    elif rsv == 2 :
        if Bxy[0] == Oxy[0] and Bxy[1] == Oxy[1] :
            B_fall = True
        elif process[Bxy[0]][Bxy[1]-1] == '.' :
            process[Bxy[0]][Bxy[1]-1] = 'B'
            process[Bxy[0]][Bxy[1]] = '.'
            Bxy[1] -= 1
        elif process[Bxy[0]][Bxy[1]-1] == 'O' :
            process[Bxy[0]][Bxy[1]] = '.'
            Bxy[1] -= 1
        
        if Rxy[0] == Oxy[0] and Rxy[1] == Oxy[1] :
            R_fall = True
        elif process[Rxy[0]][Rxy[1]-1] == '.' :
            process[Rxy[0]][Rxy[1]-1] = 'R'
            process[Rxy[0]][Rxy[1]] = '.'
            Rxy[1] -= 1
        elif process[Rxy[0]][Rxy[1]-1] == 'O' :
            process[Rxy[0]][Rxy[1]] = '.'
            Rxy[1] -= 1
            
        if (R_fall or process[Rxy[0]][Rxy[1]-1] == '#' or process[Rxy[0]][Rxy[1]-1] == 'B') and (B_fall or process[Bxy[0]][Bxy[1]-1] == '#' or process[Bxy[0]][Bxy[1]-1] == 'R') :
            return
        
    elif rsv == 3 :
        if Bxy[0] == Oxy[0] and Bxy[1] == Oxy[1] :
            B_fall = True
        elif process[Bxy[0]][Bxy[1]+1] == '.' :
            process[Bxy[0]][Bxy[1]+1] = 'B'
            process[Bxy[0]][Bxy[1]] = '.'
            Bxy[1] += 1
        elif process[Bxy[0]][Bxy[1]+1] == 'O' :
            process[Bxy[0]][Bxy[1]] = '.'
            Bxy[1] += 1
        
        if Rxy[0] == Oxy[0] and Rxy[1] == Oxy[1] :
            R_fall = True
        elif process[Rxy[0]][Rxy[1]+1] == '.' :
            process[Rxy[0]][Rxy[1]+1] = 'R'
            process[Rxy[0]][Rxy[1]] = '.'
            Rxy[1] += 1
        elif process[Rxy[0]][Rxy[1]+1] == 'O' :
            process[Rxy[0]][Rxy[1]] = '.'
            Rxy[1] += 1
            
        if (R_fall or process[Rxy[0]][Rxy[1]+1] == '#' or process[Rxy[0]][Rxy[1]+1] == 'B') and (B_fall or process[Bxy[0]][Bxy[1]+1] == '#' or process[Bxy[0]][Bxy[1]+1] == 'R') :
            return
    
    tilting(process, Rxy, Bxy, Oxy, rsv)

def decision(rsv, ex_rsv) :
    if (rsv == 0 and ex_rsv == 1) or (rsv == 1 and ex_rsv == 0) :
        return False
    elif (rsv == 2 and ex_rsv == 3) or (rsv == 3 and ex_rsv == 2) :
        return False
    else :
        return True
    
def popping() :
    processes.pop(0)
    temp_Rxy.pop(0)
    temp_Bxy.pop(0)
    temp_Oxy.pop(0)
    ex_rsv.pop(0)

processes = []
temp_Rxy = []
temp_Bxy = []
temp_Oxy = []
temp_results = []
rsv = []
ex_rsv = [-1]
processes.append(copy.deepcopy(board))
temp_Rxy.append(list([Ry, Rx]))
temp_Bxy.append(list([By, Bx]))
temp_Oxy.append(list([Oy, Ox]))
temp_results.append(0)
results = []

while processes :
    if temp_results[0] > 10 :
        temp_results.pop(0)
        popping()
        continue

    if temp_Rxy[0][0] == temp_Oxy[0][0] and temp_Rxy[0][1] == temp_Oxy[0][1] :
        if temp_Bxy[0][0] == temp_Oxy[0][0] and temp_Bxy[0][1] == temp_Oxy[0][1] :
            popping()
            temp_results.pop(0)
            
        else :
            popping()
            results.append(temp_results.pop(0))

    if not len(processes) :
        continue

    count = 0
    aroundR = around_marble(processes[0], temp_Rxy[0])
    aroundB = around_marble(processes[0], temp_Bxy[0])
    for n in range(4) :
        if aroundR[n] == 'O' :
            count += 1
            rsv.append(n)
            ex_rsv.append(n)
            
        elif aroundR[n] == '.' or aroundB[n] == '.' :
            if decision(n, ex_rsv[0]) :
                count += 1
                rsv.append(n)
                ex_rsv.append(n)

    for _ in range(count) :
        processes.append(copy.deepcopy(processes[0]))
        temp_Rxy.append(list(temp_Rxy[0]))
        temp_Bxy.append(list(temp_Bxy[0]))
        temp_Oxy.append(list(temp_Oxy[0]))
        temp_results.append(temp_results[0])

    popping()
    temp_results.pop(0)

    l = len(processes)
    
    for k in range(count) :
        tilting(processes[l-count+k], temp_Rxy[l-count+k], temp_Bxy[l-count+k], temp_Oxy[l-count+k], rsv[k])
        temp_results[l-count+k] += 1

    rsv = []

if len(results) :
    print(min(results))
else :
    print(-1)