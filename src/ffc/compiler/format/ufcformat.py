"Code generation for the UFC 1.0 format"

__author__ = "Anders Logg (logg@simula.no)"
__date__ = "2007-01-08 -- 2007-02-27"
__copyright__ = "Copyright (C) 2007 Anders Logg"
__license__  = "GNU GPL Version 2"

# UFC code templates
from ufc import *

# FFC common modules
from ffc.common.utils import *
from ffc.common.debug import *
from ffc.common.constants import *

# FFC language modules
from ffc.compiler.language.restriction import *

# FFC format modules
from codesnippets import *

# Choose map from restriction
choose_map = {Restriction.PLUS: "0_", Restriction.MINUS: "1_", None: ""}

# Specify formatting for code generation
format = { "add": lambda l: " + ".join(l),
           "subtract": lambda l: " - ".join(l),
           "multiply": lambda l: "*".join(l),
           "grouping": lambda s: "(%s)" % s,
           "bool": lambda b: {True: "true", False: "false"}[b],
           "floating point": lambda a: "%.15e" % a,
           "tmp declaration": lambda j, k: "const double " + format["tmp access"](j, k),
           "tmp access": lambda j, k: "tmp%d_%d" % (j, k),
           "comment": lambda s: "// %s" % s,
           "determinant": "det",
           "constant": lambda j: "c%d" % j,
           "coefficient table": lambda j, k: "w[%d][%d]" % (j, k),
           "coefficient": lambda j, k: "w[%d][%d]" % (j, k),
           "transform": lambda j, k, r: "J%s%d%d" % (choose_map[r], j, k),
           "inverse transform": lambda j, k, r: "Jinv%s%d%d" % (choose_map[r], j, k),
           "reference tensor" : lambda j, i, a: None,
           "geometry tensor declaration": lambda j, a: "const double " + format["geometry tensor access"](j, a),
           "geometry tensor access": lambda j, a: "G%d_%s" % (j, "_".join(["%d" % index for index in a])),
           "element tensor": lambda i, k: "A[%d]" % k,
           "dofs": lambda i: "dofs[%d]" % i,
           "entity index": lambda d, i: "c.entity_indices[%d][%d]" % (d, i),
           "num entities": lambda dim : "m.num_entities[%d]" % dim,
           "offset declaration": "unsigned int offset",
           "offset access": "offset",
           "cell shape": lambda i: {1: "ufc::line", 2: "ufc::triangle", 3: "ufc::tetrahedron"}[i]}

def init(options):
    "Initialize code generation for the UFC 1.0 format."
    pass
    
def write(code, form_data, options):
    "Generate code for the UFC 1.0 format."
    debug("Generating code for UFC 1.0")

    # Set prefix
    prefix = form_data.name

    # Generate file header
    output = ""
    output += __generate_header(prefix, options)
    output += "\n"

    # Generate code for ufc::finite_element(s)
    for i in range(form_data.num_arguments):
        output += __generate_finite_element(code[("finite_element", i)], form_data, options, prefix, i)
        output += "\n"

    # Generate code for ufc::dof_map(s)
    for i in range(form_data.num_arguments):
        output += __generate_dof_map(code[("dof_map", i)], form_data, options, prefix, i)
        output += "\n"

    # Generate code for ufc::cell_integral
    for i in range(form_data.num_cell_integrals):
        output += __generate_cell_integral(code[("cell_integral", i)], form_data, options, prefix, i)
        output += "\n"

    # Generate code for ufc::exterior_facet_integral
    for i in range(form_data.num_exterior_facet_integrals):
        output += __generate_exterior_facet_integral(code[("exterior_facet_integral", i)], form_data, options, prefix, i)
        output += "\n"
    
    # Generate code for ufc::interior_facet_integral
    for i in range(form_data.num_interior_facet_integrals):
        output += __generate_interior_facet_integral(code[("interior_facet_integral", i)], form_data, options, prefix, i)
        output += "\n"

    # Generate code for ufc::form
    output += __generate_form(code["form"], form_data, options, prefix)
    output += "\n"
    
    # Generate code for footer
    output += __generate_footer(prefix, options)

    # Write file
    filename = "%s.h" % prefix
    file = open(filename, "w")
    file.write(output)
    file.close()
    debug("Output written to " + filename)

def __generate_header(prefix, options):
    "Generate file header"

    # Check if BLAS is required
    if options["blas"]:
        blas_include = "\n#include <cblas.h>"
        blas_warning = "\n// Warning: This code was generated with '-f blas' and requires cblas.h."
    else:
        blas_include = ""
        blas_warning = ""
        
    return """\
// This code conforms with the UFC specification version 1.0
// and was automatically generated by FFC version %s.%s

#ifndef __%s_H
#define __%s_H

#include <ufc.h>%s
""" % (FFC_VERSION, blas_warning, prefix.upper(), prefix.upper(), blas_include)

def __generate_footer(prefix, options):
    "Generate file footer"
    return """\
#endif
"""

def __generate_finite_element(code, form_data, options, prefix, i):
    "Generate (modify) code for ufc::finite_element"

    ufc_code = {}

    # Set class name
    ufc_code["classname"] = "%s_finite_element_%d" % (prefix, i)

    # Generate code for members
    ufc_code["members"] = ""

    # Generate code for constructor
    ufc_code["constructor"] = "// Do nothing"

    # Generate code for destructor
    ufc_code["destructor"] = "// Do nothing"

    # Generate code for signature
    ufc_code["signature"] = "return \"%s\";" % code["signature"]

    # Generate code for cell_shape
    ufc_code["cell_shape"] = "return %s;" % code["cell_shape"]
    
    # Generate code for space_dimension
    ufc_code["space_dimension"] = "return %s;" % code["space_dimension"]

    # Generate code for value_rank
    ufc_code["value_rank"] = "return %s;" % code["value_rank"]

    # Generate code for value_dimension
    cases = ["return %s;" % case for case in code["value_dimension"]]
    ufc_code["value_dimension"] = __generate_switch("i", cases, "\nreturn 0;")

    # Generate code for evaluate_basis
    ufc_code["evaluate_basis"] = "// Not implemented"

    # Generate code for evaluate_dof
    ufc_code["evaluate_dof"] = "// Not implemented\nreturn 0.0;"

    # Generate code for inperpolate_vertex_values
    ufc_code["interpolate_vertex_values"] = "// Not implemented"

    # Generate code for num_sub_elements
    ufc_code["num_sub_elements"] = "return %s;" % code["num_sub_elements"]

    # Generate code for sub_element
    num_sub_elements = eval(code["num_sub_elements"])
    if num_sub_elements == 1:
        ufc_code["create_sub_element"] = "return new %s();" % ufc_code["classname"]
    else:
        cases = ["return new %s_sub_element_%d();" % (ufc_code["classname"], i) for i in range(num_sub_elements)]
        ufc_code = __generate_switch("i", cases, "\nreturn 0;")

    return __generate_code(finite_element_combined, ufc_code)

def __generate_dof_map(code, form_data, options, prefix, i):
    "Generate code for ufc::dof_map"

    ufc_code = {}

    # Set class name
    ufc_code["classname"] = "%s_dof_map_%d" % (prefix, i)

    # Generate code for members
    ufc_code["members"] = "\nprivate:\n\n  unsigned int __global_dimension;\n"

    # Generate code for constructor
    ufc_code["constructor"] = "__global_dimension = 0;"

    # Generate code for destructor
    ufc_code["destructor"] = "// Do nothing"

    # Generate code for signature
    ufc_code["signature"] = "return \"%s\";" % code["signature"]

    # Generate code for needs_mesh_entities
    cases = ["return %s;" % case for case in code["needs_mesh_entities"]]
    ufc_code["needs_mesh_entities"] = __generate_switch("d", cases, "\nreturn false;")

    # Generate code for init_mesh
    ufc_code["init_mesh"] = "__global_dimension = %s;\nreturn false;" % code["global_dimension"]

    # Generate code for init_cell
    ufc_code["init_cell"] = "// Do nothing"

    # Generate code for init_cell_finalize
    ufc_code["init_cell_finalize"] = "// Do nothing"

    # Generate code for global_dimension
    ufc_code["global_dimension"] = "return __global_dimension;"

    # Generate code for local dimension
    ufc_code["local_dimension"] = "return %s;" % code["local_dimension"]

    # Generate code for num_facet_dofs
    ufc_code["num_facet_dofs"] = "// Not implemented\nreturn 0;"

    # Generate code for tabulate_dofs
    ufc_code["tabulate_dofs"] = __generate_body(code["tabulate_dofs"])

    # Generate code for tabulate_facet_dofs
    ufc_code["tabulate_facet_dofs"] = "// Not implemented"

    return __generate_code(dof_map_combined, ufc_code)

def __generate_cell_integral(code, form_data, options, prefix, i):
    "Generate code for ufc::cell_integral"

    ufc_code = {}

    # Set class name
    ufc_code["classname"] = "%s_cell_integral_%d" % (prefix, i)

    # Generate code for members
    ufc_code["members"] = ""

    # Generate code for constructor
    ufc_code["constructor"] = "// Do nothing"

    # Generate code for destructor
    ufc_code["destructor"] = "// Do nothing"

    # Generate code for tabulate_tensor
    ufc_code["tabulate_tensor"]  = __generate_jacobian(form_data.cell_dimension, False)
    ufc_code["tabulate_tensor"] += "\n"
    ufc_code["tabulate_tensor"] += __generate_body(code["tabulate_tensor"])

    return __generate_code(cell_integral_combined, ufc_code)

def __generate_exterior_facet_integral(code, form_data, options, prefix, i):
    "Generate code for ufc::exterior_facet_integral"

    ufc_code = {}
    
    # Set class name
    ufc_code["classname"] = "%s_exterior_facet_integral_%d" % (prefix, i)

    # Generate code for members
    ufc_code["members"] = ""

    # Generate code for constructor
    ufc_code["constructor"] = "// Do nothing"

    # Generate code for destructor
    ufc_code["destructor"] = "// Do nothing"

    # Generate code for tabulate_tensor
    cases = [__generate_body(case) for case in code["tabulate_tensor"][1]]
    switch = __generate_switch("facet", cases)
    ufc_code["tabulate_tensor"]  = __generate_jacobian(form_data.cell_dimension, False)
    ufc_code["tabulate_tensor"] += "\n"
    ufc_code["tabulate_tensor"] += __generate_body(code["tabulate_tensor"][0])
    ufc_code["tabulate_tensor"] += "\n"
    ufc_code["tabulate_tensor"] += switch
    
    return __generate_code(exterior_facet_integral_combined, ufc_code)

def __generate_interior_facet_integral(code, form_data, options, prefix, i):
    "Generate code for ufc::interior_facet_integral"

    ufc_code = {}

    # Set class name
    ufc_code["classname"] = "%s_interior_facet_integral_%d" % (prefix, i)

    # Generate code for members
    ufc_code["members"] = ""

    # Generate code for constructor
    ufc_code["constructor"] = "// Do nothing"

    # Generate code for destructor
    ufc_code["destructor"] = "// Do nothing"

    # Generate code for tabulate_tensor, impressive line of Python code follows
    switch = __generate_switch("i", [__generate_switch("j", [__generate_body(case) for case in cases]) for cases in code["tabulate_tensor"][1]])
    ufc_code["tabulate_tensor"]  = __generate_jacobian(form_data.cell_dimension, False)
    ufc_code["tabulate_tensor"] += "\n"
    ufc_code["tabulate_tensor"] += __generate_body(code["tabulate_tensor"][0])
    ufc_code["tabulate_tensor"] += "\n"
    ufc_code["tabulate_tensor"] += switch

    return __generate_code(interior_facet_integral_combined, ufc_code)

def __generate_form(code, form_data, options, prefix):
    "Generate code for ufc::form"

    ufc_code = {}

    # Set class name
    ufc_code["classname"] = prefix

    # Generate code for members
    ufc_code["members"] = ""

    # Generate code for constructor
    ufc_code["constructor"] = "// Do nothing"

    # Generate code for destructor
    ufc_code["destructor"] = "// Do nothing"

    # Generate code for signature
    ufc_code["signature"] = "return \"%s\";" % code["signature"]

    # Generate code for rank
    ufc_code["rank"] = "return %s;" % code["rank"]

    # Generate code for num_coefficients
    ufc_code["num_coefficients"] = "return %s;" % code["num_coefficients"]

    # Generate code for create_finite_element
    num_cases = form_data.num_arguments
    cases = ["return new %s_finite_element_%d();" % (prefix, i) for i in range(num_cases)]
    ufc_code["create_finite_element"] = __generate_switch("i", cases, "\nreturn 0;")

    # Generate code for create_dof_map
    num_cases = form_data.num_arguments
    cases = ["return new %s_dof_map_%d();" % (prefix, i) for i in range(num_cases)]
    ufc_code["create_dof_map"] = __generate_switch("i", cases, "\nreturn 0;")

    # Generate code for cell_integral
    num_cases = form_data.num_cell_integrals
    cases = ["return new %s_cell_integral_%d();" % (prefix, i) for i in range(num_cases)]
    ufc_code["create_cell_integral"] = __generate_switch("i", cases, "\nreturn 0;")

    # Generate code for exterior_facet_integral
    num_cases = form_data.num_exterior_facet_integrals
    cases = ["return new %s_exterior_facet_integral_%d();" % (prefix, i) for i in range(num_cases)]
    ufc_code["create_exterior_facet_integral"] = __generate_switch("i", cases, "\nreturn 0;")

    # Generate code for interior_facet_integral
    num_cases = form_data.num_interior_facet_integrals
    cases = ["return new %s_interior_facet_integral_%d();" % (prefix, i) for i in range(num_cases)]
    ufc_code["create_interior_facet_integral"] = __generate_switch("i", cases, "\nreturn 0;")

    return __generate_code(form_combined, ufc_code)

def __generate_jacobian(cell_dimension, interior_facet):
    "Generate code for computing jacobian"

    # Choose space dimension
    if cell_dimension == 2:
        jacobian = jacobian_2D
    else:
        jacobian = jacobian_3D

    # Check if we need to compute more than one Jacobian
    if interior_facet:
        code  = jacobian % {"restriction": "0_"}
        code += "\n"
        code += jacobian % {"restriction": "1_"}
    else:
        code = jacobian % {"restriction":  ""}

    return code

def __generate_switch(variable, cases, default = ""):
    "Generate switch statement from given variable and cases"

    # Special case: no cases
    if len(cases) == 0:
        return default

    # Special case: one case
    if len(cases) == 1:
        return cases[0]

    # Create switch
    code = "switch ( %s )\n{\n" % variable
    for i in range(len(cases)):
        code += "case %d:\n%s\n  break;\n" % (i, indent(cases[i], 2))
    code += "}"
    code += default
    
    return code

def __generate_body(declarations):
    "Generate function body from list of declarations or statements"
    lines = []
    for declaration in declarations:
        if isinstance(declaration, tuple):
            lines += ["%s = %s;" % declaration]
        else:
            lines += ["%s" % declaration]
    return "\n".join(lines)

def __generate_code(format_string, code):
    "Generate code according to format string and code dictionary"

    # Fix indentation
    for key in code:
        if not key in ["classname", "members"]:
            code[key] = indent(code[key], 4)

    # Generate code
    return format_string % code
