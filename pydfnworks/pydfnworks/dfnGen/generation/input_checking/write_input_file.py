import pydfnworks.dfnGen.generation.input_checking.helper_functions as hf


def dump_params(params, output_file):
    """ Write the parameters from the verbose input file back to a simplified input file.
    """
    print(f"--> Writing parameters to file {output_file}")
    try:
        writer = open(output_file, 'w')
    except:
        hf.print_error("Check that the path of your output file is valid.")

    keys = params.keys()
    for key in keys:
        if params[key]['value'] is not None:
            if key == 'layers':
                writer.write(key + ': \n')
                for i, layer in enumerate(params['layers']['value']):

                    curl = "{"
                    for val in params['layers']['value'][i]:
                        curl += f"{val},"
                    curl = curl[:-1]
                    curl += "}"
                    writer.write(curl + '\n')

            elif key == 'regions':
                writer.write(key + ': \n')
                for i, layer in enumerate(params['regions']['value']):
                    curl = "{"
                    for val in params['regions']['value'][i]:
                        curl += f"{val},"
                    curl = curl[:-1]
                    curl += "}"
                    writer.write(curl + '\n')

            elif key == 'minimum_fracture_size':
                pass

            elif params[key]['list']:
                curl = "{"
                for val in params[key]['value']:
                    curl += f"{val},"
                curl = curl[:-1]
                curl += "}"
                writer.write(key + ': ' + curl + '\n')

            elif params[key]['type'] is bool:
                if params[key]['value']:
                    writer.write(f"{key}: 1 \n")
                else:
                    writer.write(f"{key}: 0 \n")
            else:
                writer.write(f"{key}: {params[key]['value']} \n")
        else:
            writer.write(key + ": {}\n")
