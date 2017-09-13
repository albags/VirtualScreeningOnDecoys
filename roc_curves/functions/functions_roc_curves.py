import numpy as np
import matplotlib.pyplot as plt
from sklearn import svm, datasets
from sklearn.metrics import roc_curve, auc
import csv

def curve(lista):
	"""
	Description: Compute ROC curve and ROC area for each class
	@param list with a numpy array with true and fals positives and their similarities
	@return 
		fpr : array, shape = [>2]

		    Increasing false positive rates such that element i is the false positive rate of predictions with score >= thresholds[i].

		tpr : array, shape = [>2]

		    Increasing true positive rates such that element i is the true positive rate of predictions with score >= thresholds[i].

		roc_auc : points on a curve
	"""
	y_test, y_score = np.hsplit(lista, 2)
	fpr = dict()
	tpr = dict()
	roc_auc = dict()
	fpr[0], tpr[0], _ = roc_curve(y_test[:, 0], y_score[:, 0])
	roc_auc[0] = auc(fpr[0], tpr[0])
	return fpr, tpr, roc_auc

def graphic(target, path, _list):
	"""
	Description: Plot of a ROC curve for a specific class/target
	@param 
		target : reference ligand

		path : directory where graphics will be 

		_list : list of tuplas ({fpr1, tpr1, roc_auc1, _label1}, {fpr2, tpr2, roc_auc2, _label2}, ...)

			_label : legend's description
	@return
	"""
	plt.figure()
	for fpr, tpr, roc_auc, _label in _list:
		plt.plot(fpr[0], tpr[0], label=_label+'(area = %0.2f)' % roc_auc[0])
	plt.plot([0, 1], [0, 1], 'k--')
	plt.xlim([0.0, 1.0])
	plt.ylim([0.0, 1.05])
	plt.xlabel('False Positive Rate')
	plt.ylabel('True Positive Rate')
	plt.title('Receiver operating characteristic example')
	plt.legend(loc="lower right")
	plt.savefig(path+target, format="png") 
	#plt.show()
	plt.rcParams.update({'figure.max_open_warning': 0})
	return

def leer(fileName):
	"""
	Description: Read csv file
	@param fileName
	@return 
	"""
	try: 
		with open(fileName) as f:
			output = csv.reader(f)
			for reg in output:
				print reg
	except Exception as e:
		print "Error reading the file ", fileName
	finally:
		f.close()
	return

def escribir(fileName, lista):
	"""
	Description: Write csv file
	@param fileName
		lista: information with the rows for writing the file
	@return 
	"""
	try:
		f = open(fileName, 'w')
		output = csv.writer(f)
		output.writerow(["target","usrcat","electroshape"])
		for line in lista:
			output.writerow(line)
	except Exception as e:
		print "Error writing the file ", fileName
	finally:
		f.close()
	return

def listaAverages(listNames, roc_auc, roc_auc_e):
	"""
	Description: calcule the similarity average for each target for usrcat and electroshape
	@param 
		listNames : list with all the Targets
		roc_auc/roc_auc_e : 
	@return 
		lista : list with each target, average of usrcat similarities and average for electroshape similarities
	"""
	lista = []
	i = 0
	
	for name in listNames:
		print name
		lista.append([name,roc_auc[i],roc_auc_e[i]])
		i = i+1

	return lista
