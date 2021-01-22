import requests
import click
import json


URL = 'http://217.79.62.70:8080/domains'
ONLY_ENGLISH = '^[a-zA-Z]$'


@click.command()
@click.option('--seq', help='Amino acid sequence to scan', prompt='Sequence')
@click.option('--raw', help='Get the raw output from server', is_flag=True)
@click.option('--top', help='Print domains with highest score only',
              is_flag=True)
@click.option('--output', help='File to write json output', default=None)
def send(seq, raw, top, output):
    if len(seq) > 10:
        click.echo("Too long sequence, max length 1200")
        click.echo("Aborted")
        exit(-1)

    seq = '\0' + seq + '\0'
    resp = requests.post(URL, seq).json()

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
    return resp


if __name__ == '__main__':
    send()
