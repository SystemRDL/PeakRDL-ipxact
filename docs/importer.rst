Importer
========

Importing IP-XACT definitions can occur at any point alongside normal SystemRDL
file compilation. When an IP-XACT file is imported, the register description is
loaded into the SystemRDL register model as if it were an ``addrmap`` component
declaration. Once imported, the IP-XACT contents can be used as-is, or
referenced from another RDL file.

Since the target register used internally uses SystemRDL semantics, the import
operation does a 'best effort' attempt to faithfully map the concepts described
in IP-XACT into SystemRDL objects.

The importer will automatically detect the IP-XACT standard used and will
attempt to translate as much of the document into the SystemRDL object model as
possible.

.. flat-table::
    :widths: 15 15 70
    :header-rows: 1

    *   -
        - IP-XACT
        - Resulting SystemRDL

    *   - :rspan:`4` Components
        - <memoryMap>
        - A named ``addrmap`` definition is created.

          The definition's type name is defined by the concatenation of the
          parent component's <name> and memoryMap's <name>.

          For example: ``ComponentName__MemoryMapName``

          The named definition is imported into the root SystemRDL namespace.


    *   - <addressBlock>
        - If the addressBlock's <usage> tag specifies "memory", then a named
          ``mem`` component is declared.
          Otherwise, a named ``addrmap`` is declared.

          The definition's type name is defined by the concatenation of the
          enclosing component's <name>, the parent memoryMap's <name> and
          the addressBlock's <name>.

          For example: ``ComponentName__MemoryMapName__AddressBlockName``

          The named definition is imported into the root SystemRDL namespace.

          The definition is also instantiated in the ``addrmap`` created by the
          parent memoryMap. The instance name is simply the addressBlock's <name>.

    *   - <registerFile>
        - ``regfile`` component that is anonymously declared and
          instantiated in its parent.

    *   - <register>
        - ``reg`` component that is anonymously declared and
          instantiated in its parent.

    *   - <field>
        - ``field`` component that is anonymously declared and
          instantiated in its parent reg.



    *   - :rspan:`4` Fields
        - <enumeratedValues>
        - Creates an ``enum`` definition that is assigned to
          the parent field's ``encode`` property.

    *   - <access>
        - ``sw`` property.

          If a <field> does not explicitly
          define <access>, it may inherit it from the enclosing <register> or
          <addressBlock>'s <access> tag

    *   - <testable>
        - ``donttest`` property.

    *   - <readAction>
        - ``onread`` property.

    *   - <modifiedWriteValue>
        - ``onwrite`` property.



    *   - :rspan:`2` Other
        - <displayName>
        - ``name`` property.

    *   - <description>
        - ``desc`` property.

    *   - <isPresent>
        - ``ispresent`` property.


Possible Transformations
------------------------
Some of IP-XACTs semantics are slightly more permissive than SystemRDL. Since the
importer must translate concepts to conform with SystemRDL rules, some transformations
may be performed:

* IP-XACT's rules for <name> identifiers allows for colon (:), dash (-) and
  dot (.) characters. The importer will automatically sanitize IP-XACT names
  so that they conform to SystemRDL semantics by replacing these additional
  characters with underscores (_)
* IP-XACT allows registers to be any arbitrary bit width, but SystemRDL requires
  the ``regwidth`` property to be at least 8, and a power of 2.
  The imported ``regwidth`` may be padded up as necessary.
* IP-XACT allows a register to contain multiple fields with the same name. If
  this is detected, the importer will uniquify the instance names based on the
  fields' bit ranges.



Remap States
------------
The IP-XACT standard allows a document to capture memory remap states that
describe which subsets of an address space is visible from a particular bus
interface or operational state. (See IP-XACT's <memoryRemap> elements)

Since SystemRDL is designed to only capture a monolithic snapshot of an address
space, it may be necessary to provide a ``remap_state`` parameter to the importer
in order to show otherwise hidden <addressBlock> elements.


API
---

.. autoclass:: peakrdl_ipxact.IPXACTImporter
    :special-members: __init__
    :members: import_file
