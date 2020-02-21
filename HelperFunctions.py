import subprocess


def tdd(actual, expected, test_name):
    state = "FAIL"
    result = False
    if str(actual) == str(expected):
        state = "PASS"
        result = True

    print(f"[{state}] {test_name}")
    if result is False:
        print(f"Expected: {expected}, Received: {actual}")
    return result


def call_python(call_string):
    result = subprocess.check_output(f"python {str(call_string)}", stderr=subprocess.STDOUT,
                                     universal_newlines=True).strip()
    return result
