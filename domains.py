import requests
import click
import json
from functools import reduce


URL = 'http://217.79.62.70:8080/domains'
ONLY_ENGLISH = '^[a-zA-Z]$'
MAX_LENGTH = 1200


def too_long_message():
    click.echo(f'Too long sequence, max length {MAX_LENGTH}')
    click.echo('Aborted')
    exit(-1)

@click.command()
@click.option('--seq', help='Amino acid sequence to scan', default=None)
@click.option('--raw', help='Get the raw output from server', is_flag=True)
@click.option('--top', help='Print domains with highest score only',
              is_flag=True)
@click.option('--output', help='File to write json output', default=None)
@click.option('--file', help='Input file', default=None)
@click.option('--sep', help='Separator in input file', default='\n')
@click.option('--smooth', help='Apply gaussian smoothing', is_flag=True)
@click.option('--fasta', help='Deal with input file in fasta format', is_flag=True)
def send(seq, raw, top, output, file, sep, smooth, fasta):
    if seq and file:
        click.echo('Detected multiply sources, aborted')
        exit(-1)
    elif not (seq or file):
        seq = click.prompt('Enter a sequence', type=str)

    if seq and len(seq) > MAX_LENGTH:
        too_long_message()

    if file:
        with open(file, 'r') as fd:
            if fasta:
                seq = fd.read().split(">")
                seq = seq[1:]
                for i in range(len(seq)):
                    seq[i] = seq[i].split(sep)
                    seq[i] = list(filter(len, seq[i])) # filter empty seqs
                    seq[i] = reduce(lambda y, z: y + z, seq[i][1:])
                    if len(seq[i]) > 1200:
                        too_long_message()
                
            else:
                seq = fd.read().split(sep)
                seq = list(filter(lambda x: len(x), seq)) # filter empty seqs
                for x in seq:
                    if len(x) > 1200:
                        too_long_message()
        seq = ','.join(seq)
        
    req = json.dumps({
        'sequence': seq,
        'smoothing': smooth
    })
    resp = requests.post(URL, req)
    resp = resp.json()
    resp = [resp] if not isinstance(resp, list) else resp
    orig = []

    for item in resp:
        orig.append(item["not_smoothed"])
    resp = orig

    if raw:
        click.echo(resp)
    if top:
        top_str = ''
        for item in resp:
            top_str += item['domain_id'][0] + ', '
        click.echo(top_str)
    if output:
        try:
            with open(output, 'w') as file:
                json.dump(resp, file, indent=4)
        except Exception as err:
            click.echo(f"Can't write to file {output} because of {err}")

    if not (raw or top or output):
        click.echo(resp)
    return resp


if __name__ == '__main__':
    send()