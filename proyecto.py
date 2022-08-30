def muestra_primerosGrupos(grupos):
    #Comenzamos la impresión de la agrupación primaria
    print("\n\n\n\nNúmero de Gpo.\tMintérminos\t\tExpresión en BCD")
    print ('='*60)
    for i in sorted(grupos.keys()):
        print("%5d:"%i) # Prints group number
        for j in grupos[i]:
            print("\t\t    %-20d%s"%(int(j,2),j)) # Imprime los mintérminos y su representación binaria (BCD)
        print('-'*60)
    #Término de la impresión de la agrupación primara





print('Por favor ingrese los términos separados por un espacio')
mt = [int(i) for i in input("Ingrese los mintérminos ").strip().split()]
mt.sort()
minterminos = mt
minterminos.sort()


size = len(minterminos)
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
