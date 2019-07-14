"""A Python preprocessor which allows referencing previously defined parameters.

This tries to mimic the way Lisp allows one to reference previously defined
function parameters. For example, this preprocessor enabled, one can write the
function:
    def make_rectangle(x, y, width, height=width):
        ...
Note that setting "height=width" in the above code is not valid Python and will
fail with:
    NameError: name 'width' is not defined.

To run:
    python3 -m ref_prev_params <file to run>
"""

import re
import sys
import os.path

# TODO(eugenhotaj): Compute file level tab white space instead of hardcoding.
TAB_CHARS = 4

def _build_param_to_prev_param(definition_string):
    """Builds a map of parameter name->previously defined parameter name.

    E.g.: Suppose `def_str="def my_fn(x, y=2, z=x):"`, then this function would
    return the dictionary {z: x}.

    Args:
        definition_string: A string representing a Python function definition.
    Returns:
        The map of parameters->previously defined parameters.
    """
    def_str = definition_string 
    def_str = def_str.strip().replace(' ', '')
    # TODO(eugenhotaj): Handle multi-line function definitions.
    if not def_str.endswith(':'):
        raise NotImplementedError(
                'Cannot yet handle multi-line function definitions')
    # Strip everything but the function parameters.
    def_str = def_str[def_str.find('(')+1:]
    def_str = def_str[:-2]

    params = def_str.split(',')
    param_to_prev_param = {}
    for param in params:
        if '=' in param:
            param, value = param.split("=")
            # If the value begins with a digit, period, or quote, ignore it 
            # since it's either a number or a string.
            v = value[0]
            is_constant = v.isdigit() or v == '.' or v == "'" or v == '"'
            if is_constant:
                param_to_prev_param[param] = None
            elif value in param_to_prev_param:
                param_to_prev_param[param] = value
            else:
                raise NameError("Name {} is not defined: {}".format(param,
                    definition_string))
        else:
            param_to_prev_param[param] = None
    # Filter out paramters which do not reference previous parameters.
    return {k: v for k, v in param_to_prev_param.items() if v is not None}


def preprocess(code):
    """Preprocesses the Python code to allow referencing previous parameters.

    In detail, for each function which has parameter `param` referencing the 
    previously defined parameter `prev_param`, the processor sets `param=None`
    in the function definition and inserts `param = param or prev_param` at the
    top of the function.

    E.g.: Suppose we have the following function which defaults to making
    squares if no `height` parameter is given:
        def make_rectangle(x, y, width, height=width) :
            ...
    This function would then rewrite `make_rectangle` as follows:
        def make_rectangle(x, y, width, height=None):
            height = height or width
            ...
    
    Args:
        code: Python code potentially containing function definitions with
            parameters which reference previously defined parameters.
    Returns:
        Valid Python code.
    """
    lines = code.split('\n')
    processed_lines = []
    for line in lines:
        stripped = line.strip()
        assigners = []
        # TODO(eugenhotaj): This is a very brittle check and will fail in tons
        # of cases, e.g. in comments, docstrings, etc.
        if stripped.startswith('def '):
            # Figure out how much to indent the line.
            indent = ' ' * (len(line) - len(stripped) + TAB_CHARS)
            param_to_prev_param = _build_param_to_prev_param(stripped)
            for left, right in param_to_prev_param.items():
                # TODO(eugenhotaj): This won't work if the default args are
                # separated by white space.
                line = line.replace('={}'.format(right), '=None')
                assigners.append(
                        '{0}{1} = {1} or {2}'.format(indent,  left, right))
        processed_lines.append(line)
        processed_lines.extend(assigners)
    return '\n'.join(processed_lines)


def main(argv):
    # Overwrite command line arguments to correctly pass them  to wrapped
    # program.
    sys.argv[:] = sys.argv[1:]
    progname = sys.argv[0]
    sys.path.insert(0, os.path.dirname(progname))
    with open(progname, 'r') as file_:
        code = file_.read()
        code = preprocess(code)
        code = compile(code, progname, 'exec')
    env = {
        '__file__': progname,
        '__name__': '__main__',
        '__package__': None,
        '__cached__': None,
    }
    exec(code, env)


if __name__ == '__main__':
  main(sys.argv)
