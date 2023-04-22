import json
import os

def write_to_disk(data, filename):
    """
    Write data to a JSON file on disk.

    Parameters
    ----------
    data : dict
        The data to be written to disk.
    filename : str
        The name of the file to write the data to.
    
    Returns
    -------
    None
    
    """
    with open(filename,"w") as fw:
        json.dump(data, fw, indent=4)
        print("Managing Data!")


def read_from_disk(filename):
    """
    Read data from a JSON file on disk.

    Parameters
    ----------
    filename : str
        The name of the file to read the data from.

    Returns
    -------
    dict or None
        The data read from the file, or None if the file doesn't exist.

    """
    if not os.path.exists(filename):
        return None
    with open(filename, 'r') as fw:
        data = json.load(fw)
    return data


