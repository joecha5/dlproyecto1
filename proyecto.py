import sys

# Funcion que genera una lista de minterminos dado un string separado por comas
# Recibe el nombre del archivo
# Retorna una lista con los minterminos en decimal
def generarMinterminos(archivoMin):

    archivo = open(archivoMin, "r")
    linea = archivo.read()

    mt = []
    mintermino = ""

    for i in linea:
        if i == " ":
            pass
        elif i == ",":
            mt.append(int(mintermino))
            mintermino = ""
        else:
            mintermino += i

    if(mintermino != ""):
        mt.append(int(mintermino))

    return mt

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


# Función para encontrar a los mintérminos mezclados. Por ejemplo, 10-1 son obtenidos al combinar 9(1001) y 11(1011)
# Recibe Mintermino, es una representacion del mintermino analizado para revisar cuales son los posibles terminos para este mintermino
# Retorna una lista de las posibilidades del mintermino en string
def buscaMinterminos(mintermino):
    gaps = mintermino.count('-')

    if gaps == 0: #Si no contiene - lo pasa a binario y lo envia
        return [str(int(mintermino,2))]


    x = [bin(i)[2:] for i in range(pow(2,gaps))]

    resultado = []
    
    for i in range(pow(2,gaps)):

        temp,ind = mintermino[:],-1

        for j in x[0]:
            if ind != -1:
                ind = ind+temp[ind+1:].find('-')+1
            else:
                ind = temp[ind+1:].find('-')

            temp = temp[:ind]+j+temp[ind+1:]
            
        resultado.append(str(int(temp,2)))
        x.pop(0)
    
    return resultado

# Función para checar si dos mintérminos difieren en un bit
# Recibe dos minterminos, son representaciones de minterminos en strings
# Retorna una tupla, (si difieren en un bit y el indice del bit de diferencia)
def compara(mintermino1,mintermino2):
    tmp = 0
    for i in range(len(mintermino1)):
        if mintermino1[i] != mintermino2[i]:
            mismatch_index = i
            tmp += 1
            if tmp > 1:
                return (False,None)
    return (True,mismatch_index)


# Funciona para remover mintérminos que ya fueron seleccionados previamente
# Recibe el diccionario con todos los minterminos de cada grupo y una lista con los minterminos esenciales
# No retorna nada pero modifica la variable grupos
def remueveTerminos(grupos, terms): 
    for i in terms:
        for j in buscaMinterminos(i):
            try:
                del grupos[j]
            except KeyError:
                pass


# Funcion que pasa todos los minterminos literales a su definicion binaria y los agrupa por cantidad de 1's que poseen
# Recibe el diccionario donde guarda los grupos y los minterminos ingresados en el archivo
# No retorna, modifica el diccionario de 
def agrupacionPrimaria(grupos, minterminos):
    size = len(bin(minterminos[-1]))-2
    for minterm in minterminos:
        try:
            grupos[bin(minterm).count('1')].append(bin(minterm)[2:].zfill(size)) #Append al diccionario que contiene la cantidad de 1s
        except KeyError:
            grupos[bin(minterm).count('1')] = [bin(minterm)[2:].zfill(size)] #Si no se puede agregar se crea un nuevo key con los grupos


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

# Funcion para analizar si los minterminos tienen implicantes primos y crear las tablas para los minterminos
# Recibe el diccionario de grupos y la lista de todos los implicantes primos
# Retorna una copia de los grupos actualizados, el diccionario de grupos y toda la lista de implicantes primos
def agrupacionImplicantesPrimos(grupos, all_pi):

    while True:

        tmp = grupos.copy()
        grupos,index,marcados,debo_parar = {},0,set(),True

        lista = sorted(list(tmp.keys()))
        for i in range(len(lista)-1):
            for j in tmp[lista[i]]: # Iteración a través del grupo de elementos actual 
                for k in tmp[lista[i+1]]: # Iteración a través del siguiente grupo de elementos
                    res = compara(j,k) # Comparamos los mintérminos
                    if res[0]: # Si los mintérminos difieren solamente en un bit
                        try:
                            grupos[index].append(j[:res[1]]+'-'+j[res[1]+1:]) if j[:res[1]]+'-'+j[res[1]+1:] not in grupos[index] else None # Imprimimos un guión '-' en el bit que cambia y lo agregamos al grupo correspondiente
                        except KeyError:
                            grupos[index] = [j[:res[1]]+'-'+j[res[1]+1:]] # Si el grupo no existe, crearemos un grupo al principio y pondremos un guión '-' en el cambio de bi, además de agregarlo a un nuevo grupo
                        debo_parar = False
                        marcados.add(j) # Marca el elemento j
                        marcados.add(k) # Marca el elemento k
            index += 1

        desmarcados_local = set(recorta(tmp)).difference(marcados) # Desmarcamos los elemntos de cada tabla
        all_pi = all_pi.union(desmarcados_local) # Agregamos el implicante primo a la lita global.

        print("Elementos desmarcados(Implicantes Primos) de la tabla:",None if len(desmarcados_local)==0 else ', '.join(desmarcados_local)) # Imprimimos los implicantes promos en la tabla actual
        
        if debo_parar: # Si los mintérminos no pueden ser combinados
            print("\n\n Todos los Implicantes Primos: ",None if len(all_pi)==0 else ', '.join(all_pi)) # Imprimimos todos los implicantes primos
            break

        muestra_implicantesPrimos(tmp)

    return tmp, grupos, all_pi

# Funcion para mostrar las tablas de los minterminos
# Recibe Grupos, es un diccionario con un identificador de grupo
# No Retorna nada
def muestra_implicantesPrimos(grupos):
    print("\n\n\n\nNúmero de Gpo\tMintérminos\t\tExpresión en BCD\n%s"%('='*60))
    for i in sorted(grupos.keys()):
        print("%5d:"%i) # Imprimimos el número de grupo
        for j in grupos[i]:
            print("\t\t%-24s%s"%(','.join(buscaMinterminos(j)),j)) # Imprimimos los mintérminos y su representación binaria.
        print('-'*60)

# Funcion para la impresión y procesamiento de los implicantes primos 
# Recibe la lista de implicantes, la longitud del implicante mas largo, el diccionario modificado anteriormente y el diccionario de inicio
# No retorna nada, modifica chart que es el diccionario final
def procesarImplicantes(all_pi, longitud, chart, mt):

    for i in all_pi:

        minterminos_mezclados,y = buscaMinterminos(i),0
        print("%-16s|"%','.join(minterminos_mezclados),end='')

        for j in minterminos_mezclados:

            x = mt.index(int(j))*(longitud+1) # La posicioón donde debemos de marcar con una x
            print(' '*abs(x-y)+' '*(longitud-1)+'X',end='')
            y = x+longitud

            try:
                chart[j].append(i) if i not in chart[j] else None # Agregamos el mintérmino a la impresión
            except KeyError:
                chart[j] = [i]

        print('\n'+'-'*(len(mt)*(longitud+1)+16))

# Funcion main, se encarga de toda la logica para el llamado de los metodos ateriores
# Recibe 2 strings, el nombre del archivo con los minterminos y nombre del pdf a generar
# No retorna nada
def main(archivoMin, nombrePDF):

    # Inicia el programa con el archivo y genera los minterminos dentro del archivo
    mt = generarMinterminos(archivoMin)
    mt.sort()
    minterminos = mt
    minterminos.sort()

    grupos,all_pi = {},set()

    # Proceso para crear los grupos y pasarlo a binario
    agrupacionPrimaria(grupos, minterminos)
    muestra_primerosGrupos(grupos)

    # Proceso para crear las tablas y encontrar los implicantes primos     
    tmp, grupos, all_pi = agrupacionImplicantesPrimos(grupos, all_pi)

    # Comenzamos la impresión y procesamiento de los implicantes primos 
    longitud = len(str(mt[-1])) # El número de los dígitos del mintérmino más largo
    chart = {}
    print('\n\n\nImpresión de los implicantes primos escenciales:\n\n  Mintérminos  |%s\n%s'%(' '.join((' '*(longitud-len(str(i))))+str(i) for i in mt),'='*(len(mt)*(longitud+1)+16)))
    procesarImplicantes(all_pi, longitud, chart, mt)

    IPE = BuscarIPE(chart) # Encontramos los implicantes primos escenciales
    print("\nImplicantes Primos Escenciales: "+', '.join(str(i) for i in IPE))
    remueveTerminos(chart,IPE) #Removemos los Implicantes Primos Escenciales de las columnas relacionadas de la impresión
    
    resultado_final = [BuscarVariables(i) for i in IPE] # Resultado Final solamente con los Implicantes Primos Escenciales
    print('\nSolución: F = '+' + '.join(''.join(i) for i in resultado_final))

    input("\nPresione enter para salir y generar el PDF")


if __name__ == "__main__":
    main(sys.argv[2], sys.argv[4])