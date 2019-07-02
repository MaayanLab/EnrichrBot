import json
import requests
import pprint
import pandas as pd
import time


def read_file(filename):
    df = pd.read_csv(filename, sep='\t')
    rsid_lst = df.copy().rsID.tolist()
    rsid_lst = [x[2:] for x in rsid_lst]
    return rsid_lst

def run_query(rsid):
    DBSNP_URL = 'https://api.ncbi.nlm.nih.gov/variation/v0/refsnp/'
    response = requests.get(DBSNP_URL + rsid)
    if not response.ok:
        raise Exception('Error during query')
    data = json.loads(response.text)
    if 'primary_snapshot_data' in data.keys():
        gene_data = data['primary_snapshot_data']['allele_annotations'][0]['assembly_annotation'][0]['genes']
        gene_symbol = [gene_data[i]['locus'] for i in range(len(gene_data))]
    if 'merged_snapshot_data' in data.keys():
        new_rsid = data['merged_snapshot_data']['merged_into'][0]
        gene_symbol = run_query(new_rsid)
    if 'nosnppos_snapshot_data' in data.keys() or 'withdrawn_snapshot_data' in data.keys() or 'unsupported_snapshot_data' in data.keys():
        return []
    return gene_symbol

def run(filename):
    rsids = read_file(filename)
    result = []
    for i in range(len(rsids)):
        gene_symbol = run_query(rsids[i])
        result.append(['rs' + str(rsids[i]), gene_symbol])
        time.sleep(1)
    final_df = pd.DataFrame.from_records(result, columns=['rsID', 'gene_ID'])
    return final_df

def write(dataframe, outfile):
    dataframe.to_csv(outfile, sep='\t', index=False, header=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='input file with SNPs and rsIDs, rsIDs must be in column named \'rsID\'')
    parser.add_argument('-o', '--output', default=sys.stdout, help='name the output file, default will print to screen')
    args = parser.parse_args()
    res = run(args.input)
    if args.output:
        write(res, args.output)
    else:
        print(res)
