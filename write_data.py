import os

def save_ols_results(results, name):
	o = open("output/ols/" + name + ".out", 'w+')
	for result in results:
		o.write(result + '\n')
	o.close()

def save_plots(plots, name):
	os.mkdir("output/scatters/" + name)
	for i in range(len(plots)):
		figi      = plots[i][0]
		plot_name = plots[i][1]
		figi.savefig("output/scatters/"+name+"/"+str(i)+"-"+plot_name+".png",
		 format='png', dpi=500)

def save_validation(validation_list):
	o = open("validation/validation_vals.out", 'w+')
	for validation in validation_list:
		o.write("X Indices: " + str(validation[2]) + "\n" + "Y Index: " + str(validation[3]) + "\n"+ 'K-folds Score: ' + str(validation[0] * 100) + '% ' + '\n' + 'AIC Score: ' + str(validation[1]) + '\n\n')
	o.close()
