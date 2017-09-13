from functions import functions_roc_curves
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc
import pymongo
from pymongo import MongoClient
import os

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
	collection = db.usrcat
	coll = db.electroshape

	list_targets = collection.find({}, {"_target":1,"_id":0})
	list_names = [name["_target"] for name in list_targets]
	listaCsv = []

	for target in list_names:
		try:
			print target;
			cursor_usrcat = collection.find({"_target":target})
			cursor_electroshape = coll.find({"_target":target})
			for i in cursor_electroshape:
				for mol in i["similarities"]:
					if mol["molid"].startswith("CHEMBL"):
						molid_ref = "CHEMBL"
						break
					elif mol["molid"].startswith("ZINC"):
						molid_ref = "ZINC"
						break
					else:
						continue

			cursor_electroshape.rewind()

			# Calcul lists with usrcat and electroshape 
			if molid_ref == "CHEMBL":
				usrcat_list = np.array([(1, mol["similarity"]) if mol["molid"].startswith("CHEMBL") else (0, mol["similarity"]) for i in cursor_usrcat for mol in i["similarities"] ])
				electroshape_list = np.array([(1, mol["similarity"]) if mol["molid"].startswith("CHEMBL") else (0, mol["similarity"]) for i in cursor_electroshape for mol in i["similarities"] ])
			elif molid_ref == "ZINC":
				usrcat_list = np.array([(0, mol["similarity"]) if mol["molid"].startswith("ZINC") else (1, mol["similarity"]) for i in cursor_usrcat for mol in i["similarities"] ])
				electroshape_list = np.array([(0, mol["similarity"]) if mol["molid"].startswith("ZINC") else (1, mol["similarity"]) for i in cursor_electroshape for mol in i["similarities"] ])

			# Compute ROC curve and ROC area for the target for usrcat
			fpr, tpr, roc_auc = functions_roc_curves.curve(usrcat_list)

			# Compute ROC curve and ROC area for the target for electroshape
			fpr_e, tpr_e, roc_auc_e = functions_roc_curves.curve(electroshape_list)
			
			#List roc curves for representation
			list_roc_curves = [];
			_label = ""

			_label="ROC curve for usrcat"
			list_roc_curves.append((fpr,tpr,roc_auc,_label))

			_label="ROC curve for electroshape"
			list_roc_curves.append((fpr_e,tpr_e,roc_auc_e,_label))
			
			# Plot of a ROC curve for a specific target in usrcat and electroshape
			path = "./graphics/"

			functions_roc_curves.graphic(target, path, list_roc_curves)
						
			#List with all the targets and the roc_auc for usrcat and electroshape for writing the csv file 
			listaCsv.append([target, roc_auc[0], roc_auc_e[0]])
			

		except Exception as e:
			print target, "error ROC curve calculation"
			continue
		
	try:	
		#Write and read the csv file
		fileName = "simAverage.csv"

		functions_roc_curves.escribir(fileName,listaCsv)
		functions_roc_curves.leer(fileName)

	except Exception as e:
			print target, "error writing/reading csv file"
			

if __name__ == "__main__":
	main()
