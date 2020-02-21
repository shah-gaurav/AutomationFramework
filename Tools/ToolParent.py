from abc import ABC, abstractmethod
from ErrorHandling import ErrorHandler as err


class ToolParent(ABC):

    # These are the args that are required by your tool (change each of the below consts to be whatever you need)
    # NOTE:  THe "-tool <tool_name>" arg name and value have already been stripped by Automator.py
    REQUIRED_ARG_NAMES = []
    # Arg names that must have values.  May be the complete set of REQUIRED_ARG_NAMES or may be a subset
    REQUIRED_ARG_VALUES = []
    # These are args that are usually flags (do not require values, but may have them).  May or may not be set
    OPTIONAL_ARG_NAMES = []
    # These are args that are optional but do require a value if set
    OPTIONAL_ARG_VALUES = []

    def __init__(self, arg_list):

        self.__set_err_usage(type(self).__name__, self.REQUIRED_ARG_NAMES, self.REQUIRED_ARG_VALUES, self.OPTIONAL_ARG_NAMES,
                             self.OPTIONAL_ARG_VALUES)

        self.arg_pairs = {}
        self.arg_names = []

        index = 0
        num_args = len(arg_list)
        try:
            while index < num_args:
                # Format of arg list should be [-<arg_name> [<arg_value>] .. -<arg_name> [<arg_value>]]
                # Every arg name must start with '-'.  Arg values are optional.  Arg values cannot start with '-'.
                # Arg values must follow an arg name.
                # NOTE:  All arg names and arg values will be stored as lower case to make them case independent
                if arg_list[index][0] == "-":
                    # [1:] notation means char 1 forward (0 based)
                    arg_name_without_dash = arg_list[index][1:].lower()
                    # All arg names are stored in arg_names list
                    self.arg_names.append(arg_name_without_dash)

                    # If there are more args, do a quick look ahead to see if next item is another arg name (will start
                    # with '-') or if it's an arg value (no '-').  Store arg value and arg name in arg_pairs.
                    next_arg_index = index + 1
                    if next_arg_index < num_args and arg_list[next_arg_index][0] != "-":
                        self.arg_pairs[arg_name_without_dash] = arg_list[next_arg_index].lower(
                        )
                        index += 1  # Skip the arg value in the iteration of arg names and arg values
                    index += 1  # Move to the next arg name
                else:
                    # Reaching this condition means either the list started with an arg value or the list
                    # had two arg values in a row.  Both conditions are incorrect.
                    # index + 3 is used because 0 = script name, 1 = '-tool', 2 = tool name.
                    err.error_abort(f"ERROR: Arg value #{index+3} '{arg_list[index]}' not preceded by arg name.",
                                    True)
        except IndexError:
            err.error_abort(
                f"ERROR: Incorrect argument list.\n{err.get_call_script_string()}", True)

        self.validate_arguments(self.REQUIRED_ARG_NAMES, self.REQUIRED_ARG_VALUES,
                                self.OPTIONAL_ARG_NAMES, self.OPTIONAL_ARG_VALUES)

        self.arguments = {}
        # load argument information into object variables
        try:

            for arg in self.REQUIRED_ARG_NAMES:
                if arg in self.REQUIRED_ARG_VALUES:
                    self.arguments[arg] = self.__get_value(arg)
                else:
                    self.arguments[arg] = True if self.__optional_arg_set(
                        arg) else False

            for arg in self.OPTIONAL_ARG_NAMES:
                if arg in self.OPTIONAL_ARG_VALUES:
                    if self.__optional_arg_set(arg):
                        self.arguments[arg] = self.__get_value(arg)
                    else:
                        self.arguments[arg] = None
                else:
                    self.arguments[arg] = True if self.__optional_arg_set(
                        arg) else False

        except Exception as e:
            err.error_abort(e, True)
        return

    def __get_value(self, arg_name):
        # Although caller should use lower case, go ahead and force it lower to be case independent
        lower_name = arg_name.lower()
        if lower_name in self.arg_pairs:
            return self.arg_pairs[lower_name]
        else:
            raise Exception(f"ERROR: '{arg_name}' does not have a value pair")

    @abstractmethod
    def validate_arguments(self, name_list, value_name_list, optional_name_list, optional_value_list):
        # Make all names lower case (do not change values)
        for local_list in (name_list, value_name_list, optional_name_list, optional_value_list):
            index = 0
            while index < len(local_list):
                local_list[index] = local_list[index].lower()
                index += 1

        for name in name_list:
            err.assert_abort(name in self.arg_names,
                             f"ERROR: '{name}' is a required argument", True)
        for name in value_name_list:
            err.assert_abort(name in self.arg_pairs,
                             f"ERROR: '{name}' requires a value", True)
        # Optional name list is a bit trickier.  Need to remove all required names first then compare
        # each optional name to the optional list.  I.e. are the non-required names in the list 'allowed'
        # by the optional list?
        remaining_names = []
        for name in self.arg_names:
            if name not in name_list:
                remaining_names.append(name)
        for name in remaining_names:
            err.assert_abort(name in optional_name_list,
                             f"ERROR: '{name}' is not a valid argument", True)
            # Is a valid optional arg.  If also in optional_value_list then it must have a value
            if name in optional_value_list:
                err.assert_abort(name in self.arg_pairs,
                                 f"ERROR: '{name}' requires a value", True)

    def __optional_arg_set(self, optional_arg):
        return optional_arg.lower() in self.arg_names

    def get_argument_value(self, arg):
        return self.arguments[arg.lower()]

    @staticmethod
    def __set_err_usage(class_name, required_arg_names, required_arg_values, optional_arg_names, optional_arg_values):
        usage_msg = f"-tool {class_name} "
        for arg in required_arg_names:
            if arg in required_arg_values:
                usage_msg += f"-{arg} <value> "
            else:
                usage_msg += f"-{arg} "

        for optional_arg in optional_arg_names:
            if optional_arg in optional_arg_values:
                usage_msg += f"[-{optional_arg} <value>] "
            else:
                usage_msg += f"[-{optional_arg}] "

        err.set_usage_message(usage_msg.rstrip())
