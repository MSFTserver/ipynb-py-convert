import json
import sys
from os import path

header_comment = '# %%\n'

def nb2py(notebook):
    result = []
    cells = notebook['cells']

    for cell in cells:
        cell_type = cell['cell_type']
        metadata = cell['metadata']
        format_metadata = json.dumps(metadata,indent=2).split("\n")
        reformat_metadata = '# !! {"metadata":'
        for key in format_metadata:
            if key == '{':
                reformat_metadata+=f"{key}\n"
            elif key == '}':
                reformat_metadata+="# !! "+key+"}\n"
            else:
                reformat_metadata+=f'# !! {key}\n'
    
        if cell_type == 'markdown':
            result.append('%s"""\n%s\n"""'%
                          (header_comment+reformat_metadata, ''.join(cell['source'])))

        if cell_type == 'code':
            result.append("%s%s" % (header_comment+reformat_metadata, ''.join(cell['source'])))

    return '\n\n'.join(result)


def py2nb(py_str):
    # remove leading header comment
    if py_str.startswith(header_comment):
        py_str = py_str[len(header_comment):]

    cells = []
    chunks = py_str.split('\n\n%s' % header_comment)

    for chunk in chunks:
        cell_type = 'code'
        new_json = {'metadata':{}}
        if chunk.startswith('# !!'):
            new_json = json.loads("\n".join([x.strip() for x in chunk.splitlines() if '# !!' in x]).replace('# !!',''))
            chunk = "\n".join([x for x in chunk.splitlines() if '# !!' not in x])
        if chunk.startswith("'''"):
            chunk = chunk.strip("'\n")
            cell_type = 'markdown'
        elif chunk.startswith('"""'):
            chunk = chunk.strip('"\n')
            cell_type = 'markdown'

        cell = {
            'cell_type': cell_type,
            'metadata': new_json['metadata'],
            'source': chunk.splitlines(True),
        }

        if cell_type == 'code':
            cell.update({'outputs': [], 'execution_count': None})

        cells.append(cell)

    notebook = {
        'cells': cells,
        'metadata': {
            'anaconda-cloud': {},
            'accelerator': 'GPU',
            'colab': {
              'collapsed_sections': [
                'CreditsChTop',
                'TutorialTop',
                'CheckGPU',
                'InstallDeps',
                'DefMidasFns',
                'DefFns',
                'DefSecModel',
                'DefSuperRes',
                'AnimSetTop',
                'ExtraSetTop'
              ],
              'machine_shape': 'hm',
              'name': 'Disco Diffusion v5.1 [w/ Turbo]',
              'private_outputs': True,
              'provenance': [],
              'include_colab_link': True
            },
            'kernelspec': {
              'display_name': 'Python 3',
              'language': 'python',
              'name': 'python3'
            },
            'language_info': {
              'codemirror_mode': {
                'name': 'ipython',
                'version': 3
              },
              'file_extension': '.py',
              'mimetype': 'text/x-python',
              'name': 'python',
              'nbconvert_exporter': 'python',
              'pygments_lexer': 'ipython3',
              'version': '3.6.1'
            }
          },
          'nbformat': 4,
          'nbformat_minor': 4
    }

    return notebook


def convert(in_file, out_file):
    _, in_ext = path.splitext(in_file)
    _, out_ext = path.splitext(out_file)

    if in_ext == '.ipynb' and out_ext == '.py':
        with open(in_file, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        py_str = nb2py(notebook)
        with open(out_file, 'w', encoding='utf-8') as f:
            f.write(py_str)

    elif in_ext == '.py' and out_ext == '.ipynb':
        with open(in_file, 'r', encoding='utf-8') as f:
            py_str = f.read()
        notebook = py2nb(py_str)
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=2)

    else:
        raise(Exception('Extensions must be .ipynb and .py or vice versa'))


def main():
    argv = sys.argv
    if len(argv) < 3:
        print('Usage: ipynb-py-convert in.ipynb out.py')
        print('or:    ipynb-py-convert in.py out.ipynb')
        sys.exit(1)

    convert(in_file=argv[1], out_file=argv[2])


if __name__ == '__main__':
    main()
