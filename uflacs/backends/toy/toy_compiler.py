

# FIXME: This file probably needs a massive rewrite.



import ufl
from ufl.classes import Argument
from ufl.algorithms import expand_derivatives, expand_compounds

from uflacs.utils.tictoc import TicToc
from uflacs.utils.log import error

from uflacs.codeutils.format_code_structure import Block, format_code_structure

from uflacs.generation.compiler import compile_expression_partitions
from uflacs.generation.generate import generate_code_from_ssa, generate_expression_code, generate_expression_body

from uflacs.backends.toy.toy_language_formatter import ToyCppLanguageFormatter
from uflacs.backends.toy.toy_statement_formatter import ToyCppStatementFormatter

from uflacs.params import default_parameters

def compile_expression(expr, prefix=""):
    "Toy compiler, translating an expression to a block of code that is not quite compilable."

    parameters = default_parameters() # FIXME: Get as input

    # Preprocess expression
    # TODO: Use ufl ExprData preprocessing, unify expr data with form data:
    expr = expand_compounds(expr)
    expr = expand_derivatives(expr,
                              apply_expand_compounds_before=False,
                              apply_expand_compounds_after=False,
                              use_alternative_wrapper_algorithm=False)

    # FIXME: Preprocess expression grad2localgrad etc.

    # Compile expression into intermediate representation (partitions in ssa form)
    partitions_ir = compile_expression_partitions(expr, parameters)

    # FIXME: Hack to automatically disable integral accumulation in statement formatter
    partitions_ir["entitytype"] = None

    # Build code representation
    code, dummy_coefficient_names = generate_expression_code(partitions_ir,
                                                             {},
                                                             {},
                                                             ToyCppLanguageFormatter,
                                                             ToyCppStatementFormatter)

    # Wrap in a block for readability
    code = Block(code)

    # Format code representation into a single string
    formatted = format_code_structure(code)
    return formatted

def compile_form(form, prefix=""):
    "Toy compiler, translating a Form to a block of code that is not quite compilable."

    parameters = default_parameters() # FIXME: Get as input

    # Preprocess form
    form_data = form.compute_form_data()

    # We'll place all code in a list while building the program
    code = []

    # Generate code for each integral
    k = 0
    for ida in form_data.integral_data:
        for integral in ida.integrals:
            integrand = integral.integrand()

            # TODO: Unify this code with compile_expression:
            expr = integrand
            object_names = form_data.object_names
            form_argument_mapping = form_data.function_replace_map

            # FIXME: Preprocess expression grad2localgrad etc.

            # Compile expression into intermediate representation (partitions in ssa form)
            partitions_ir = compile_expression_partitions(expr, parameters)

            # Build code representation
            integral_code, dummy_coefficient_names = generate_expression_code(partitions_ir,
                                                                              form_argument_mapping,
                                                                              object_names,
                                                                              ToyCppLanguageFormatter,
                                                                              ToyCppStatementFormatter)

            # Wrap in a block for readability
            code.append(['',Block(integral_code),''])

    # Format code representation into a single string
    formatted = format_code_structure(code)
    return formatted

def compile_element(element, prefix=""):
    return "// Toy compiler has no element support. Element repr: %r" % (element,)
