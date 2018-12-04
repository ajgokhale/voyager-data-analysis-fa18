import os

def save_ols_results(results, name):
	o = open("output/ols/ols-" + name + ".out", 'w+')
	for result in results:
		o.write(result + '\n')
	o.close()

def save_plots(plots, name):
	os.mkdir("output/scatters/" + name)
	for plot in plots:
		figi      = plot[0]
		plot_name = plot[1]
		figi.savefig("output/scatters/"+name+"/"+plot_name+".png", format='png')