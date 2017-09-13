from cStringIO import StringIO
from rdkit import Chem
from rdkit.Chem import AllChem
import operator
import os
import pymongo

def clean_sdf(archivo, ruta):
	"""
	Process the file .sdf and return a string with the data cleaned.
	"""
	try:
		if os.stat(ruta+'/'+archivo).st_size > 0:
			with open(ruta+'/'+archivo,'r') as fd:
				fcontent = fd.read()
			fd.close()
			final_sdf_list = [m + '$$$$\n' for m in fcontent.split('$$$$\n') if m.endswith('END\n')]
			final_sdf = ''.join(final_sdf_list)
			return (final_sdf)
		else:
			print "Empty URL file ... existing", ruta, archivo
			return 
	except OSError:
		print "URL file missing", ruta, archivo
		return

def load_molecule(final_sdf):
	"""
	Extract the molecule from the data cleaned
	"""
	mol_ligand = Chem.ForwardSDMolSupplier(StringIO(final_sdf), removeHs=False)
	return (mol_ligand)

def update_bbdd(nombre, similarities, collection):
	"""
	Update the data base with the similarities found. If the crystal ligand is wrong it register 
	the molecule with a message
	"""
	if (similarities):
		for i in similarities:
			collection.update_one(
				{"_target": nombre},
				{
				"$addToSet": {"similarities": {"molid": i[0], "similarity": i[1]}}
				},
				upsert=True
			)
			print i[0], "conformer inserted"
	else:
		collection.update_one(
				{"_target": nombre},
				{
					"$addToSet": {"similarities": "error calcul moments_ligand"}
				},
				upsert=True
			)
	return

def sort_similarities(total_similarities):
	"""
	Sort the similirities
	"""
	return sorted(total_similarities.iteritems(), key=operator.itemgetter(1))

