import platform
import hashlib
import os
import ctypes


def get_platform_info():
    info = platform.uname()
    return '&'.join([
        info.system,
        info.node,
        info.release,
        info.version,
        info.machine,
        info.processor
    ])


def write_hidden(file_name, data):
    FILE_ATTRIBUTE_HIDDEN = 0x02
    # For *nix add a '.' prefix.
    # prefix = '.' if os.name != 'nt' else ''
    # file_name = prefix + file_name if file_name[0] != '.' else file_name
    prefix = '.'
    file_name = prefix + file_name

    # Write file.
    with open(file_name, 'w') as f:
        f.write(data)

    # For windows set file attribute.
    if os.name == 'nt':
        ret = ctypes.windll.kernel32.SetFileAttributesW(
            file_name,
            FILE_ATTRIBUTE_HIDDEN
        )
        if not ret:  # There was an error.
            raise ctypes.WinError()


def create_info_file():
    hasher = hashlib.sha256()
    info_string = get_platform_info()
    hasher.update(info_string.encode('utf-8'))

    fp = hasher.hexdigest()
    write_hidden('platforminfo', fp)

    return fp


def get_fp():
    try:
        with open('.platforminfo', 'r') as file:
            fp = file.read()
        return fp
    except FileNotFoundError:
        return create_info_file()


if __name__ == '__main__':
    print(get_fp())
