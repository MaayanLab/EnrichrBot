import subprocess as sp
import multiprocessing as mp

with open("significantSNPfiles.txt", "r") as fp:
  filenames = fp.readlines()
filenames = [x.strip() for x in filenames]
outfiles = [x[:x.rfind('_')] + '_genes.csv' for x in filenames]

def run(index):
    cmd_nocutoff = "python3 ~/Desktop/EnrichrBot/nearestgene_cutoff.py " + filenames[index] + " -o ../geneSets_nocutoff/" + outfiles[index]
    cmd_2k_05k = "python3 ~/Desktop/EnrichrBot/nearestgene_cutoff.py " + filenames[index] + " -o ../geneSets_2k_0.5k/" + outfiles[index] + " -u 2000 -d 500"
    cmd_2k_2k = "python3 ~/Desktop/EnrichrBot/nearestgene_cutoff.py " + filenames[index] + " -o ../geneSets_2k_2k/" + outfiles[index] + " -u 2000 -d 2000"
    cmd_5k_5k = "python3 ~/Desktop/EnrichrBot/nearestgene_cutoff.py " + filenames[index] + " -o ../geneSets_5k_5k/" + outfiles[index] + " -u 5000 -d 5000"
    cmd_20k_20k = "python3 ~/Desktop/EnrichrBot/nearestgene_cutoff.py " + filenames[index] + " -o ../geneSets_20k_20k/" + outfiles[index] + " -u 20000 -d 20000"
    cmd_100k_100k = "python3 ~/Desktop/EnrichrBot/nearestgene_cutoff.py " + filenames[index] + " -o ../geneSets_100k_100k/" + outfiles[index] + " -u 100000 -d 100000"
    cmd_200k_200k = "python3 ~/Desktop/EnrichrBot/nearestgene_cutoff.py " + filenames[index] + " -o ../geneSets_200k_200k/" + outfiles[index] + " -u 200000 -d 200000"
    cmd_500k_500k = "python3 ~/Desktop/EnrichrBot/nearestgene_cutoff.py " + filenames[index] + " -o ../geneSets_500k_500k/" + outfiles[index] + " -u 500000 -d 500000"
    # sp.call(cmd_nocutoff, shell=True)
    # sp.call(cmd_2k_05k, shell=True)
    sp.call(cmd_2k_2k, shell=True)
    # sp.call(cmd_5k_5k, shell=True)
    # sp.call(cmd_20k_20k, shell=True)
    # sp.call(cmd_100k_100k, shell=True)
    # sp.call(cmd_200k_200k, shell=True)
    # sp.call(cmd_500k_500k, shell=True)

if __name__ == '__main__':
    pool = mp.Pool(processes=10)
    pool.map(run, range(len(filenames)))
