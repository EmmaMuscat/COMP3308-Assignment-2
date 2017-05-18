#!/usr/bin/python3

from operator import itemgetter

import sys
import math
import csv

def read_data(fname):
	lines = []
	with open(fname) as f:
		lines = f.readlines()
	return lines

def get_data(fname):
	lines = read_data(fname)

	data = []
	for line in lines:
		line = line.strip()
		data.append(line.split(","))

	for dt in data:
		for i in range(0,len(dt)):
			if i != 8:
				dt[i] = float(dt[i])

	return data

def Euclidean_d(training_dt,input_dt):
	sum = 0
	for i in range(0,len(input_dt)):
		sum = sum + math.pow(training_dt[i]-input_dt[i],2)

	return math.sqrt(sum)

def KNN(k,training_dt,input_dt):
	ls = []

	for train_dt in training_dt:
		dis = Euclidean_d(train_dt,input_dt)
		ls.append({"distance":dis,"class":train_dt[8]})

	pound  = []
	for elmt in ls:
		if (len(pound) < k):
			pound.append(elmt)
			pound = sorted(pound,key=itemgetter("distance"),reverse=True)
		else:
			for el in pound:
				if elmt["distance"] < el["distance"]:
					el["distance"] = elmt["distance"]
					el["class"] = elmt["class"]
					break
			pound = sorted(pound,key=itemgetter("distance"),reverse=True)

	factor = 0
	for elmt in pound:
		if elmt["class"] == "yes":
			factor = factor + 1
		elif elmt["class"] == "no":
			factor = factor - 1

	if factor >= 0:
		return "yes"
	else:
		return "no"

def get_mean(data):
	sum = []
	for i in range(0,8):
		sum.append({"yes":0,"no":0})
	num_of_yes = 0
	for dt in data:
		if dt[8] == "yes":
			num_of_yes = num_of_yes + 1
			for i in range(0,len(dt)-1):
				sum[i]["yes"] = sum[i]["yes"] + dt[i]
		elif dt[8] == "no":
			for i in range(0,len(dt)-1):
				sum[i]["no"] = sum[i]["no"] + dt[i]

	mean = []
	for num in sum:
		mean_yes = num["yes"]/num_of_yes
		mean_no = num["no"]/(len(data)-num_of_yes)
		mean.append({"yes":mean_yes,"no":mean_no})

	mean.append(num_of_yes)

	return mean

def get_standard_deviation(training_dt,mean):
	sum = []
	for i in range(0,8):
		sum.append({"yes":0,"no":0})
	for dt in training_dt:
		for i in range(0,len(dt)-1):
			num = math.pow(dt[i] - mean[i][dt[8]],2)
			sum[i][dt[8]] = sum[i][dt[8]] + num

	standard_deviation = []
	for num in sum:
		standard_deviation_yes = math.sqrt(num["yes"]/(mean[-1]-1))
		standard_deviation_no = math.sqrt(num["no"]/(len(training_dt)-mean[-1]-1))
		standard_deviation.append({"yes":standard_deviation_yes,"no":standard_deviation_no})

	return standard_deviation

def probability_density_function(mean,standard_deviation,x):
	result = (1/(standard_deviation*math.sqrt(2*math.pi))) * math.exp(-math.pow(x-mean,2)/(2*math.pow(standard_deviation,2)))

	return result

def BN(training_dt,input_dt):
	mean = get_mean(training_dt)
	standard_deviation = get_standard_deviation(training_dt,mean)

	num_of_yes = mean[-1]

	result = []
	for dt in input_dt:
		probability_yes = []
		probability_no = []
		for i in range(0,len(dt)):
			probability_yes.append(probability_density_function(mean[i]["yes"],standard_deviation[i]["yes"],dt[i]))
			probability_no.append(probability_density_function(mean[i]["no"],standard_deviation[i]["no"],dt[i]))
		x_yes = num_of_yes/len(training_dt)
		x_no = (len(training_dt) - num_of_yes)/len(training_dt)
		for p in probability_yes:
			if p != 0:
				x_yes = x_yes * p
		for p in probability_no:
			if p != 0:
				x_no = x_no * p

		if x_no > x_yes:
			result.append("no")
		else:
			result.append("yes")

	return result

def get_algo(algo,training_dt,input_dt):
	result = []
	if algo == "NB":
		result = BN(training_dt,input_dt)
	elif "NN" in algo:
		k = int(algo.strip("NN"))
		for in_dt in input_dt:
			result.append(KNN(k,training_dt,in_dt))
	else:
		return 1

	return result

def print_result(result):
	for rs in result:
		print (rs)

def folds(training_dt):
	ls_yes = []
	ls_no = []
	for dt in training_dt:
		if dt[8] == "yes":
			ls_yes.append(dt)
		elif dt[8] == "no":
			ls_no.append(dt)

	folds = []
	for i in range(0,10):
		folds.append([])

	len_yes = int(len(ls_yes)/10)
	rmd_yes = len(ls_yes)%10
	len_no = int(len(ls_no)/10)
	rmd_no = len(ls_no)%10

	for i in range(0,10):
		for j in range(0,len_yes):
			folds[i].append(ls_yes.pop(0))
		for j in range(0,len_no):
			folds[i].append(ls_no.pop(0))

	for i in range(0,10):
		if (len(ls_yes) > 0):
			folds[i].append(ls_yes.pop(0))
		if (len(ls_no) > 0):
			folds[i].append(ls_no.pop(0))


	with open('pima-CSV.csv', 'w', newline='') as myfile:
		wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
		for fold in folds:
			wr.writerow(["fold"])
			for row in fold:
				wr.writerow(row)

def main(argv):
	if (len(argv) != 3):
		return 1

	training_file = argv[0]
	input_file = argv[1]
	algo = argv[2]


	training_dt = get_data(training_file)
	input_dt = get_data(input_file)

	#folds(training_dt)

	result = get_algo(algo,training_dt,input_dt)

	print_result(result)

if __name__ == "__main__":
   main(sys.argv[1:])