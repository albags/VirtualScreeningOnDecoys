import functions.common_functions
from electroshape.toolkits.rd import generate_moments
from electroshape import similarity
import pymongo
from pymongo import MongoClient
import os
from os import walk
import argparse

def calc_moments(archivo, ruta):
	"""
	Generate moments for the content of each file
	"""
	final_sdf = common_functions.clean_sdf(archivo, ruta)
	mol_ligand = common_functions.load_molecule(final_sdf)
	if(mol_ligand):
		moments = []
		for mol in mol_ligand: 
			moment = generate_moments(mol)
			moments.append(moment)
	return moments

def find_similarity(archivo, nombreArchivo, moments_ligand, ruta):
	"""
	Calcule similarities for each crystal ligand with all his conformers (actives and decoys)
	"""
	similar = []
	similarities = {}
	moments_conformer = calc_moments(archivo, ruta)
	try:
		for i in range(len(moments_ligand)):
			for j in range(len(moments_conformer)):
				simil = similarity.es_sim_score(moments_ligand[i], moments_conformer[j])
				similar.append(simil)
		max_sim = max(similar)
		similarities[nombreArchivo] = max_sim
		return similarities
	except Exception as e:
		pass


#PROGRAM
def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("-p", "--path", help="PATH", required=True)
	opts = parser.parse_args()
	return opts

def main():

#Connection to Mongo DB
	try:
		conn=pymongo.MongoClient()
		print "Connected successfully!!!\n"
	except pymongo.errors.ConnectionFailure, e:
		print "Could not connect to MongoDB: %s" % e 

#Usar base de datos
	db = conn.DUDE
#Usar una coleccion
	collection = db.electroshape

	opts = parse_args()
	listDir = os.walk(opts.path)
	for (ruta, ficheros, archivos) in listDir:
		total_similarities = {}
		for fichero in ficheros:
			if(fichero == "conformers"):
				nombre_mol =  os.path.basename(ruta)
				print "\nTarget:", nombre_mol
				listDir_c = os.walk(ruta)
				moments_ligand = []
				if (collection.find_one({"_target": nombre_mol})):
					print "Target existente"
					break
				for (ruta_2, ficheros_2, archivos_2) in listDir_c:
					for archivo in archivos_2:
						(nombreArchivo, extension) = os.path.splitext(archivo)
						if (ruta_2.endswith("conformers")):
							if(extension == ".sdf" and nombreArchivo == "crystal_ligand"):
								try:
									moments_ligand = calc_moments(archivo, ruta_2)
								except:
									common_functions.update_bbdd(nombre_mol, False, collection)
									print "error moments_ligand"
									break
						elif (ruta_2.endswith(("conformers/decoys", "conformers/actives"))):
							try:
								similarities = find_similarity(archivo, nombreArchivo, moments_ligand, ruta_2)
								total_similarities.update(similarities)
							except:
								print nombre_mol, "Error calcul similarity"
				sort_sim = common_functions.sort_similarities(total_similarities)
				common_functions.update_bbdd(nombre_mol, sort_sim, collection)  

	print "finish"

if __name__ == "__main__":
	main()
