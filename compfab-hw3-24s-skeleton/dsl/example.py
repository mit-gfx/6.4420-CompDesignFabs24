# An example script to use your DSL and compile to an SVG

from tab import Tab, generate_root_tab, generate_child_tab, draw_svg

root = generate_root_tab()
# child1 = generate_child_tab(root, ...)
# child2 = generate_child_tab(root, ...)
# child3 = generate_child_tab(child1, ...)

draw_svg(root, "example.svg")