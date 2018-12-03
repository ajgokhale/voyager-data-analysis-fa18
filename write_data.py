def save_ols_results(results, name):
	o = open("output/ols/ols-" + name + ".out", 'w+')
	for result in results:
		o.write(result + '\n')
	o.close()