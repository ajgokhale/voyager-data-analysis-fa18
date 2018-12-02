def save_ols_results(results):
	o = open("output/ols.out", 'w+')
	for result in results:
		o.write(str(result) + '\n')
	o.close()