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
print (grupos)
