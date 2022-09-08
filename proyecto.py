from pylatex import Document, Section, Subsection, Tabular, Command
from pylatex import NewPage
from pylatex.utils import NoEscape
import pdflatex
import sys

# Funcion que genera una lista de minterminos dado un el nomobre del archivo donde viene un string separado por comas
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
def muestra_primerosGrupos(grupos, doc):
    with doc.create(Section('Primer Paso')):
        doc.append("Paso 1: ")
        doc.append("\nPara el primer paso se pasan los minterminos a su representacion Binaria y se procese a agrupar en una tabla por su cantidad de 1's")
        doc.append("\n\n\n")
        with doc.create(Subsection('Tabla agrupada de minterminos')):
            with doc.create(Tabular('| c | c | c |')) as table:
                table.add_hline()
                table.add_row(('Grupo', 'Mintermino', 'Binario'))
                table.add_hline()
                
                for i in sorted(grupos.keys()):
                    table.add_row((i, '', ''))

                    for j in grupos[i]:
                        table.add_row(('', int(j,2), j))
                    
                    table.add_hline()

                table.add_hline()

    '''print("\n\n\n\nNúmero de Gpo.\tMintérminos\t\tExpresión en BCD\n%s"%('='*60))
    for i in sorted(grupos.keys()):
        print("%5d:"%i) 
        for j in grupos[i]:
            print("\t\t    %-20d%s"%(int(j,2),j)) # Imprime los mintérminos y su representación binaria (BCD)
        print('-'*60)'''

# Funcion para analizar si los minterminos tienen implicantes primos y crear las tablas para los minterminos
# Recibe el diccionario de grupos y la lista de todos los implicantes primos
# Retorna una copia de los grupos actualizados, el diccionario de grupos y toda la lista de implicantes primos
def agrupacionImplicantesPrimos(grupos, all_pi, doc):

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

        stringTmp = "De la tabla anterior se pueden obtener Elementos que son Implicantes Primos: "
        if len(desmarcados_local) == 0:
            pass
        else:
            stringTmp += ', '.join(desmarcados_local)

        doc.append(stringTmp)
        
        if debo_parar: # Si los mintérminos no pueden ser combinados
            break

        muestra_implicantesPrimos(grupos, doc)

    return tmp, grupos, all_pi

# Funcion para mostrar las tablas de los minterminos
# Recibe Grupos, es un diccionario con un identificador de grupo
# No Retorna nada
def muestra_implicantesPrimos(grupos, doc):

    doc.append("\n\n")

    with doc.create(Subsection('Tabla agrupada de minterminos')):
        with doc.create(Tabular('| c | c | c |')) as table:
            table.add_hline()
            table.add_row(('Grupo', 'Mintermino', 'Binario'))
            table.add_hline()
            
            for i in sorted(grupos.keys()):
                table.add_row((i, '', ''))

                for j in grupos[i]:
                    table.add_row(('', ', '.join(buscaMinterminos(j)), j))
                
                table.add_hline()

            table.add_hline()
        doc.append("\n\n")
    

    '''
    print("\n\n\n\nNúmero de Gpo\tMintérminos\t\tExpresión en BCD\n%s"%('='*60))
    for i in sorted(grupos.keys()):
        print("%5d:"%i) # Imprimimos el número de grupo
        for j in grupos[i]:
            print("\t\t%-24s%s"%(','.join(buscaMinterminos(j)),j)) # Imprimimos los mintérminos y su representación binaria.
        print('-'*60)
        '''

# Funcion para la impresión y procesamiento de los implicantes primos 
# Recibe la lista de implicantes, la longitud del implicante mas largo, el diccionario modificado anteriormente y el diccionario de inicio
# No retorna nada, modifica chart que es el diccionario final
def procesarImplicantes(all_pi, longitud, chart, mt, doc):

    column = "| "
    for i in range(len(mt)+1):
        column += "c |"

    doc.append("\n\n")

    with doc.create(Subsection('Tabla procesar minterminos')):

        with doc.create(Tabular(column)) as table:

            table.add_hline()
            tupla = ["Mintermino"]

            for i in mt:
                tupla.append(str(i))

            tupla = tuple(tupla)

            table.add_row(tupla)
            table.add_hline()
            
            for i in all_pi:

                minterminos_mezclados,y = buscaMinterminos(i),0
                tuplaAux = []

                stringTmp2 = ','.join(minterminos_mezclados)

                tuplaAux.append(stringTmp2)
                for j in minterminos_mezclados:
                    for k in range(len(mt)):
                        if(len(tuplaAux) <= len(mt)):
                            tuplaAux.append(" ")
                        if k == mt.index(int(j)):
                            try:
                                tuplaAux[k+1] = "X"
                            except:
                                tuplaAux.append("X")
                    try:
                        chart[j].append(i) if i not in chart[j] else None # Agregamos el mintérmino a la impresión
                    except KeyError:
                        chart[j] = [i]

                table.add_row(tuple(tuplaAux))
                table.add_hline()

        doc.append("\n\n")


    

# Funcion main, se encarga de toda la logica para el llamado de los metodos ateriores
# Recibe 2 strings, el nombre del archivo con los minterminos y nombre del pdf a generar
# No retorna nada
def main(archivoMin, nombrePDF):

    # Configuracoin del doc y creacion del mismo
    geometry_options = {"tmargin": "1cm", "lmargin": "1cm", "margin": "1cm"}
    doc = Document(geometry_options=geometry_options, documentclass="beamer")

    # Crea la primera pagina del doc con el titulo y las cosas necesarias
    with doc.create(Section('Titlepage')):
        doc.preamble.append(Command('title', 'Implementación del algoritmo de Quine-McCluskey'))
        doc.preamble.append(Command('author', 'Sebastian Hidalgo, Daniela Quesada, Joel Chavarria'))
        doc.preamble.append(Command('date', NoEscape(r'\today')))
        doc.append(NoEscape(r'\maketitle'))

    doc.append(NewPage())

    # Inicia el programa con el archivo y genera los minterminos dentro del archivo
    mt = generarMinterminos(archivoMin)
    mt.sort()
    minterminos = mt
    minterminos.sort()

    with doc.create(Section('Quine-McCluskey')):
        doc.append('Quine-McCluskey')
        doc.append('\n\nEl procedimiento de Quine-McClusky parte del hecho de que una ecuación booleana está descrita por sus mintérminos.')
        doc.append('\n\nPara el ejemplo a elaborar se utilizan los siguientes minterminos: ')
        doc.append(str(minterminos))

    doc.append(NewPage())

    grupos,all_pi = {},set()

    # Proceso para crear los grupos y pasarlo a binario
    agrupacionPrimaria(grupos, minterminos)
    muestra_primerosGrupos(grupos, doc)

    doc.append(NewPage())


    with doc.create(Section("Segundo paso")):
        doc.append("Paso 2:")
        doc.append("\nPara el siguiente paso se analizan los implicantes primos de cada grupo, asi mismo tambien se crean las tablas de estos mismos con su representacion y se saca cada implicante por grupo.\n\n")
        # Proceso para crear las tablas y encontrar los implicantes primos     
        tmp, grupos, all_pi = agrupacionImplicantesPrimos(grupos, all_pi, doc)
    
    doc.append(NewPage())

    with doc.create(Section("Tercer paso")):
        doc.append("Paso 3:")
        doc.append("\nPara el siguiente paso se muestran todos los implicantes primos que se han encontrado, luego se crea una tabla donde se representan estos minterminos esenciales y se muestran para que mintermino es esencial.\n\n")

    # Comenzamos la impresión y procesamiento de los implicantes primos 
        longitud = len(str(mt[-1])) # El número de los dígitos del mintérmino más largo
        chart = {}

        stringTmp = "Todos los Implicantes Primos: "

        if len(all_pi) == 0:
            None
        else:
            stringTmp += ', '.join(all_pi)

        doc.append(stringTmp)

        procesarImplicantes(all_pi, longitud, chart, mt, doc)

    doc.append(NewPage())

    with doc.create(Section("Cuarto paso")):
        doc.append("Paso 4:")
        doc.append("\nPara el siguiente paso se toman todos los implicantes luego de analizarlos anteriormente y simplificar respectiamente las posiciones de la X. \nLuego se muestra la funcion correspondiente simplificada. \n\n")

        IPE = BuscarIPE(chart) # Encontramos los implicantes primos escenciales
        stringTmp1 = "Implicantes Primos Escenciales: " + ', '.join(str(i) for i in IPE)
        doc.append(stringTmp1)
        doc.append("\n")
        remueveTerminos(chart,IPE) #Removemos los Implicantes Primos Escenciales de las columnas relacionadas de la impresión
    
        resultado_final = [BuscarVariables(i) for i in IPE] # Resultado Final solamente con los Implicantes Primos Escenciales
        stringTmp2 = 'Solución: F = '+' + '.join(''.join(i) for i in resultado_final)
        doc.append(stringTmp2)


    input("\nPresione enter para salir y generar el PDF")
    doc.generate_pdf(nombrePDF, clean_tex=False, compiler='pdfLaTex')


if __name__ == "__main__":
    main(sys.argv[2], sys.argv[4])