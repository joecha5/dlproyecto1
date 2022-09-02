# Funcion para mostrar los primeros grupos
# Recibe Grupos, es un diccionario con un identificador de grupo que separa por cantidad de 1's en cada mintermino
# No Retorna nada
def muestra_primerosGrupos(grupos):
    print("\n\n\n\nNúmero de Gpo.\tMintérminos\t\tExpresión en BCD\n%s"%('='*60))
    for i in sorted(grupos.keys()):
        print("%5d:"%i) 
        for j in grupos[i]:
            print("\t\t    %-20d%s"%(int(j,2),j)) # Imprime los mintérminos y su representación binaria (BCD)
        print('-'*60)

# Funcion para encontrar los implicantes primos esenciales
# Recibe Grupos, es un diccionario con un identificador de grupo que separa por cantidad de 1's en cada mintermino
# Retorna una lista de los minterminos
def BuscarIPE(grupos):
    resultado = []
    for i in grupos:
        if len(grupos[i]) == 1:
            if grupos[i][0] not in resultado:
                resultado.append(grupos[i][0]) 
            else: 
                None
    return resultado

# Función para encontrar las variables en los términos. Por ejemplo, el mintérmino --01 tiene a C' y D como variables
# Recibe Mintermino, es una representacion del mintermino analizado para revisar cuales son las variables
# Retorna una lista de variables del mintermino como en el ejemplo mostrado retorna [C',D]
def BuscarVariables(mintermino):
    lista_variables = []
    for i in range(len(mintermino)):
        if mintermino[i] == '0':
            lista_variables.append(chr(i+65)+"'")
        elif mintermino[i] == '1':
            lista_variables.append(chr(i+65))
    return lista_variables

# Funcion para recortar los minterminos que son iguales, recibe grupos
# Recibe Grupos, es un diccionario con un identificador de grupo que separa por cantidad de 1's en cada mintermino
# Retorna una lista de los minterminos eliminando los que son iguales
def recorta(grupos):
    elementos_recortados = []
    for i in grupos:
        elementos_recortados.extend(grupos[i])
    return elementos_recortados


def buscaMinterminos(a): # Función para encontrar a los mintérminos mezclados. Por ejemplo, 10-1 son obtenidos al combinar 9(1001) y 11(1011)
    print("buscaMinterminos: ", a)
    gaps = a.count('-')
    if gaps == 0:
        return [str(int(a,2))]
    x = [bin(i)[2:].zfill(gaps) for i in range(pow(2,gaps))]
    temp = []
    for i in range(pow(2,gaps)):
        temp2,ind = a[:],-1
        for j in x[0]:
            if ind != -1:
                ind = ind+temp2[ind+1:].find('-')+1
            else:
                ind = temp2[ind+1:].find('-')
            temp2 = temp2[:ind]+j+temp2[ind+1:]
        temp.append(str(int(temp2,2)))
        x.pop(0)
    return temp

def compara(a,b): # Función para checar si dos mintérminos difieren en un bit
    c = 0
    for i in range(len(a)):
        if a[i] != b[i]:
            mismatch_index = i
            c += 1
            if c>1:
                return (False,None)
    return (True,mismatch_index)

def remueveTerminos(_chart,terms): # Remueve mintérminos que ya fueron seleccionados previamente
    for i in terms:
        for j in buscaMinterminos(i):
            try:
                del _chart[j]
            except KeyError:
                pass


def main():
    ##Aca comienza el main

    print('Por favor ingrese los términos separados por un espacio')
    mt = [int(i) for i in input("Ingrese los mintérminos ").strip().split()]
    mt.sort()
    minterminos = mt
    minterminos.sort()


    size = len(bin(minterminos[-1]))-2
    grupos,all_pi = {},set()


    # Comenzamos la agrupación primaria
    for minterm in minterminos:
        try:
            grupos[bin(minterm).count('1')].append(bin(minterm)[2:].zfill(size)) #Append al diccionario que contiene la cantidad de 1s
        except KeyError:
            grupos[bin(minterm).count('1')] = [bin(minterm)[2:].zfill(size)] #Si no se puede agregar se crea un nuevo key con los grupos
    # Término de la agrupación primaria
    # grupos = {cantidad de 1s: [grupos que solo tengan esa cantidad]}

    muestra_primerosGrupos(grupos)


    # Proceso para crear las tablas y encontrar los implicantes primos 
    while True:
        tmp = grupos.copy()
        grupos,m,marcados,debo_parar = {},0,set(),True
        l = sorted(list(tmp.keys()))
        for i in range(len(l)-1):
            for j in tmp[l[i]]: # Iteración a través del grupo de elementos actual 
                for k in tmp[l[i+1]]: # Iteración a través del siguiente grupo de elementos
                    res = compara(j,k) # Comparamos los mintérminos
                    if res[0]: # Si los mintérminos difieren solamente en un bit
                        try:
                            grupos[m].append(j[:res[1]]+'-'+j[res[1]+1:]) if j[:res[1]]+'-'+j[res[1]+1:] not in grupos[m] else None # Imprimimos un guión '-' en el bit que cambia y lo agregamos al grupo correspondiente
                        except KeyError:
                            grupos[m] = [j[:res[1]]+'-'+j[res[1]+1:]] # Si el grupo no existe, crearemos un grupo al principio y pondremos un guión '-' en el cambio de bi, además de agregarlo a un nuevo grupo
                        debo_parar = False
                        marcados.add(j) # Marca el elemento j
                        marcados.add(k) # Marca el elemento k
            m += 1
        desmarcados_local = set(recorta(tmp)).difference(marcados) # Desmarcamos los elemntos de cada tabla
        all_pi = all_pi.union(desmarcados_local) # Agregamos el implicante primo a la lita global.
        print("Elementos desmarcados(Implicantes Primos) de la tabla:",None if len(desmarcados_local)==0 else ', '.join(desmarcados_local)) # Imprimimos los implicantes promos en la tabla actual
        if debo_parar: # Si los mintérminos no pueden ser combinados
            print("\n\nAll Implicantes Primos: ",None if len(all_pi)==0 else ', '.join(all_pi)) # Imprimimos todos los implicantes primos
            break
        # Imprimimos en todos los grupos siguientes
        print("\n\n\n\nNúmero de Gpo\tMintérminos\t\tExpresión en BCD\n%s"%('='*60))
        for i in sorted(grupos.keys()):
            print("%5d:"%i) # Imprimimos el número de grupo
            for j in grupos[i]:
                print("\t\t%-24s%s"%(','.join(buscaMinterminos(j)),j)) # Imprimimos los mintérminos y su representación binaria.
            print('-'*60)
        # Terminamos la impresión de los grupos siguientes
    # Terminamos el proceso de la creación de tablas y encontrar los implicantes primos


    # Comenzamos la impresión y procesamiento de los implicantes primos 
    sz = len(str(mt[-1])) # El número de los dígitos del mintérmino más largo
    chart = {}
    print('\n\n\nImpresión de los implicantes primos escenciales:\n\n  Mintérminos  |%s\n%s'%(' '.join((' '*(sz-len(str(i))))+str(i) for i in mt),'='*(len(mt)*(sz+1)+16)))
    for i in all_pi:
        minterminos_mezclados,y = buscaMinterminos(i),0
        print("%-16s|"%','.join(minterminos_mezclados),end='')
        for j in minterminos_mezclados:
            x = mt.index(int(j))*(sz+1) # La posicioón donde debemos de marcar con una x
            print(' '*abs(x-y)+' '*(sz-1)+'X',end='')
            y = x+sz
            try:
                chart[j].append(i) if i not in chart[j] else None # Agregamos el mintérmino a la impresión
            except KeyError:
                chart[j] = [i]
        print('\n'+'-'*(len(mt)*(sz+1)+16))
    # Terminamos la impresión y procesamiento de los implicantes primos

    IPE = BuscarIPE(chart) # Encontramos los implicantes primos escenciales
    print("\nImplicantes Primos Escenciales: "+', '.join(str(i) for i in IPE))
    remueveTerminos(chart,IPE) #Removemos los Implicantes Primos Escenciales de las columnas relacionadas de la impresión
    
    if(len(chart) == 0): # Si los imintérminos premanecen después de remover los Implicantes Primos de las columnas relacionadas
        resultado_final = [BuscarVariables(i) for i in IPE] # Resultado Final solamente con los Implicantes Primos Escenciales
    print('\nSolución: F = '+' + '.join(''.join(i) for i in resultado_final))

    input("\nPresione enter para salir ")


if __name__ == "__main__":
    main()