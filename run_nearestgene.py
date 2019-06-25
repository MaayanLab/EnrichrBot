import subprocess as sp
import multiprocessing as mp

with open("significantSNPfiles.txt", "r") as fp:
  filenames = fp.readlines()
filenames = [x.strip() for x in filenames]
outfiles = [x[:x.rfind('_')] + '_genes.csv' for x in filenames]

def run(index):
    cmd = "python3 ~/Desktop/EnrichrBot/nearestgene_cutoff.py " + filenames[index] + " -o ../geneSets_nocutoff/" + outfiles[index]
    sp.call(cmd, shell=True)

if __name__ == '__main__':
    pool = mp.Pool(processes=10)
    pool.map(run, range(len(filenames)))
