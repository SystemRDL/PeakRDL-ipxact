
# Examples!

## Convert a SystemRDL file to IP-XACT

Use the `convert_to_ipxact.py` example script to translate SystemRDL into IP-XACT:

```
./convert_to_ipxact.py my_subblock.rdl
```

Results in the creation of the equivalent IP-XACT file: `my_subblock.xml`

## Import IP-XACT into a bigger design

The `print_hierarchy.py` example from the systemrdl-compiler project has been
enhanced to be able to read in a mix of SystemRDL and IP-XACT files. See how
you can instantiate the contents of an IP-XACT file in a top-level RDL file.

```
./print_hierarchy.py my_subblock.xml top.rdl
```

Results in the following output:

```
 my_top_design
         my_subblock_inst
                 reg1
                         [0:0] f1 sw=rw
                         [15:8] f2 sw=rw
                 reg_array[0]
                         [0:0] x sw=rw
                 reg_array[1]
                         [0:0] x sw=rw
                 reg_array[2]
                         [0:0] x sw=rw
                 reg_array[3]
                         [0:0] x sw=rw
         other_reg
                 [31:0] x sw=rw
```