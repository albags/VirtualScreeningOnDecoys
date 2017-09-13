from functions import functions_roc_curves
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc
from sklearn.metrics import average_precision_score
import os
import pymongo
from pymongo import MongoClient


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

	cursor_usrcat = collection.find()
	cursor_electroshape = coll.find()

	try:
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

		y_test, y_score = np.hsplit(usrcat_list, 2)
		print average_precision_score(y_test, y_score)  

		y_test_e, y_score_e = np.hsplit(electroshape_list, 2)
		print average_precision_score(y_test_e, y_score_e)  

		# Compute ROC curve and ROC area for the target for usrcat
		fpr, tpr, roc_auc = functions_roc_curves.curve(usrcat_list)

		# Compute ROC curve and ROC area for the target for electroshape
		fpr_e, tpr_e, roc_auc_e = functions_roc_curves.curve(electroshape_list)
		
		# List roc curves for representation
		list_roc_curves = [];
		_label = ""

		_label="ROC average curve for usrcat"
		list_roc_curves.append((fpr,tpr,roc_auc,_label))

		_label="ROC average curve for electroshape"
		list_roc_curves.append((fpr_e,tpr_e,roc_auc_e,_label))

		# Plot of a ROC curve for a specific target in usrcat and electroshape
		path = "./graphics/"
		target = "Average"

		#functions_roc_curves.graphic(target, path, list_roc_curves)

	except Exception as e:
		print "error"

if __name__ == '__main__':
	main()