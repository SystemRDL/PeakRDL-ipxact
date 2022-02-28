from typing import Optional, List, Iterable, Dict, Any, Type, Union, Set
import re

from collections import OrderedDict
from xml.dom import minidom

from systemrdl import RDLCompiler, RDLImporter
from systemrdl import rdltypes
from systemrdl.messages import SourceRefBase
from systemrdl import component as comp

from . import typemaps

class IPXACTImporter(RDLImporter):

    def __init__(self, compiler: RDLCompiler):
        super().__init__(compiler)
        self.ns = None # type: str
        self._current_regwidth = 32
        self._addressUnitBits = 8
        self._current_addressBlock_access = rdltypes.AccessType.rw
        self.remap_states_seen = set() # type: Set[str]

    @property
    def src_ref(self) -> SourceRefBase:
        return self.default_src_ref

    #---------------------------------------------------------------------------
    def import_file(self, path: str, remap_state: Optional[str] = None) -> None:
        super().import_file(path)

        # minidom does not provide file position data. Using a bare SourceRef
        # for everything created during this import
        self._current_regwidth = 32
        self._addressUnitBits = 8
        self.remap_states_seen = set()

        dom = minidom.parse(path)

        addressBlock_s = self.seek_to_top_addressBlocks(dom, remap_state)

        # Parse all the addressBlock elements found
        addrmap_or_mems = []
        for addressBlock in addressBlock_s:
            addrmap_or_mem = self.parse_addressBlock(addressBlock)
            if addrmap_or_mem is not None:
                addrmap_or_mems.append(addrmap_or_mem)

        if not addrmap_or_mems:
            self.msg.fatal(
                "'memoryMap' must contain at least one 'addressBlock' element",
                self.src_ref
            )

        if (len(addrmap_or_mems) == 1) and (addrmap_or_mems[0].addr_offset == 0):
            # OK to drop the hierarchy implied by the enclosing memoryMap
            # since it is only a wrapper around a single addressBlock at base
            # offset 0
            # This addressBlock will be the top component that is registered
            # in $root
            top_component = addrmap_or_mems[0]

            #  de-instantiate the addrmap
            top_component.type_name = top_component.inst_name
            top_component.is_instance = False
            top_component.inst_name = None
            top_component.original_def = None
            top_component.external = None
            top_component.inst_src_ref = None
            top_component.addr_offset = None

        else:
            # memoryMap encloses multiple addressBlock components, or the single
            # one uses a meaningful address offset.
            # In order to preserve this information, encapsulate them in a
            # top-level parent that is named after the memoryMap

            # Get the top-level memoryMap's element values
            d = self.flatten_element_values(addressBlock_s[0].parentNode)

            # Check for required name
            if 'name' not in d:
                self.msg.fatal("memoryMap is missing required tag 'name'", self.src_ref)

            # Create component instance to represent the memoryMap
            C = comp.Addrmap()
            C.def_src_ref = self.src_ref

            # Collect properties and other values
            C.type_name = d['name']

            if 'displayName' in d:
                self.assign_property(C, "name", d['displayName'])

            if 'description' in d:
                self.assign_property(C, "desc", d['description'])

            # Insert all the addrmap_or_mems as children
            C.children = addrmap_or_mems

            top_component = C

        # register it with the root namespace
        self.register_root_component(top_component)

    #---------------------------------------------------------------------------
    def seek_to_top_addressBlocks(self, dom: minidom.Element, remap_state: Optional[str]) -> List[minidom.Element]:
        """
        IP-XACT files can be a little ambiguous depending on who they come from
        This function returns the most reasonable starting point to use
        as the top-level node for import.

        Returns a list of addressBlock elements

        If:
            - There is exactly one memoryMap
            - Inside it, a single addressBlock
        Then the addressBlock is the top-level node
        (will actually return a list with only one addressBlock)

        If:
            - There is exactly one memoryMap
            - Inside it, more than one addressBlock that has meaningful contents
                "meaningful" is having a name, base address, and at least one
                child
        Then the memoryMap is the top-level node
        (will actually return a list of remaining meaningful addressBlocks)

        If there is more than one memoryMap, use the first one that contains
        an addressBlock child
        """

        # Find <component> and determine namespace prefix
        c_ipxact = self.get_first_child_by_tag(dom, "ipxact:component")
        c_spirit = self.get_first_child_by_tag(dom, "spirit:component")
        if c_ipxact is not None:
            component = c_ipxact
        elif c_spirit is not None:
            component = c_spirit
        else:
            self.msg.fatal(
                "Could not find a 'component' element",
                self.src_ref
            )
        self.ns = component.prefix

        # Find <memoryMaps>
        memoryMaps_s = self.get_children_by_tag(component, self.ns+":memoryMaps")
        if len(memoryMaps_s) != 1:
            self.msg.fatal(
                "'component' must contain exactly one 'memoryMaps' element",
                self.src_ref
            )
        memoryMaps = memoryMaps_s[0]

        # Find all <memoryMap>
        memoryMap_s = self.get_children_by_tag(memoryMaps, self.ns+":memoryMap")

        # Find the first <memoryMap> that has at least one <addressBlock>
        for mm in memoryMap_s:
            addressBlock_s = self.get_children_by_tag(mm, self.ns+":addressBlock")
            addressBlock_s += self.get_remapped_address_blocks(mm, remap_state)
            if addressBlock_s:
                parent_memoryMap = mm
                break
        else:
            self.msg.error(
                "Could not find any 'memoryMap' elements that contained an importable register space",
                self.src_ref
            )

            if self.remap_states_seen:
                self.msg.warning(
                    "Contains the following possible memory remap states: \n\t%s\n"
                    "Try selecting a remap state, as it may uncover state-specific address regions."
                    % "\n\t".join(self.remap_states_seen),
                    self.src_ref
                )

            self.msg.fatal(
                "Import failed",
                self.src_ref
            )


        aub = self.get_first_child_by_tag(parent_memoryMap, self.ns+":addressUnitBits")
        if aub:
            self._addressUnitBits = self.parse_integer(get_text(aub))

            if (self._addressUnitBits < 8) or (self._addressUnitBits % 8 != 0):
                self.msg.fatal(
                    "Importer only supports <addressUnitBits> that is a multiple of 8",
                    self.src_ref
                )


        return addressBlock_s

    #---------------------------------------------------------------------------
    def get_remapped_address_blocks(self, memoryMap: minidom.Element, remap_state: Optional[str]) -> List[minidom.Element]:
        """
        A memoryMap can also contain one or more addressBlocks that are wrapped in a memoryRemap tag.
        These provide alternate views into the address space depending on the state of the device.
        This function returns a list of addressBlock elements that match the remap state
        """
        memoryRemaps = self.get_children_by_tag(memoryMap, self.ns+":memoryRemap")
        addressBlocks = []

        for memoryRemap in memoryRemaps:
            this_remapState = memoryRemap.getAttribute(self.ns+":state")
            self.remap_states_seen.add(this_remapState)
            if this_remapState == remap_state:
                remap_addressBlocks = self.get_children_by_tag(memoryRemap, self.ns+":addressBlock")
                addressBlocks.extend(remap_addressBlocks)
        return addressBlocks

    #---------------------------------------------------------------------------
    def parse_addressBlock(self, addressBlock: minidom.Element) -> Union[comp.Addrmap, comp.Mem]:
        """
        Parses an addressBlock and returns an instantiated addrmap or mem
        component.

        If addressBlock is empty or usage specifies 'reserved' then returns
        None
        """
        # Schema:
        #   {nameGroup}
        #       name (required) --> inst_name
        #       displayName --> prop:name
        #       description --> prop:desc
        #   accessHandles
        #   isPresent --> prop:ispresent
        #   baseAddress (required) --> addr_offset
        #   {addressBlockDefinitionGroup}
        #       typeIdentifier
        #       range (required) --> divide by width and set prop:mementries if Mem
        #       width (required) --> prop:memwidth if Mem
        #       {memoryBlockData}
        #           usage --> Mem vs Addrmap instance
        #           volatile
        #           access --> prop:sw if Mem
        #           parameters
        #       {registerData}
        #           register --> children
        #           registerFile --> children
        #   vendorExtensions

        d = self.flatten_element_values(addressBlock)

        if d.get('usage', None) == "reserved":
            # 1685-2014 6.9.4.2-a.1.iii: defines the entire range of the
            # addressBlock as reserved or for unknown usage to IP-XACT. This
            # type shall not contain registers.
            return None

        # Check for required values
        required = {'name', 'baseAddress', 'range', 'width'}
        missing = required - set(d.keys())
        for m in missing:
            self.msg.fatal("addressBlock is missing required tag '%s'" % m, self.src_ref)

        # Create component instance
        is_memory = (d.get('usage', None) == "memory")

        if is_memory:
            C = self.instantiate_mem(
                self.create_mem_definition(),
                d['name'], self.AU_to_bytes(d['baseAddress'])
            )
        else:
            C = self.instantiate_addrmap(
                self.create_addrmap_definition(),
                d['name'], self.AU_to_bytes(d['baseAddress'])
            )

        # Collect properties and other values
        if 'displayName' in d:
            self.assign_property(C, "name", d['displayName'])

        if 'description' in d:
            self.assign_property(C, "desc", d['description'])

        if 'isPresent' in d:
            self.assign_property(C, "ispresent", d['isPresent'])

        self._current_regwidth = d['width']
        if is_memory:
            self.assign_property(C, "memwidth", d['width'])
            self.assign_property(
                C, "mementries",
                (d['range'] * self._addressUnitBits) // (d['width'])
            )

            if 'access' in d:
                self.assign_property(C, "sw", d['access'])

        if 'access' in d:
            self._current_addressBlock_access = d['access']
        else:
            self._current_addressBlock_access = rdltypes.AccessType.rw

        # collect children
        for child_el in d['child_els']:
            if child_el.localName == "register":
                R = self.parse_register(child_el)
                if R:
                    self.add_child(C, R)
            elif child_el.localName == "registerFile" and not is_memory:
                R = self.parse_registerFile(child_el)
                if R:
                    self.add_child(C, R)
            else:
                self.msg.error(
                    "Invalid child element <%s> found in <%s:addressBlock>"
                    % (child_el.tagName, self.ns),
                    self.src_ref
                )

        if 'vendorExtensions' in d:
            C = self.addressBlock_vendorExtensions(d['vendorExtensions'], C)

        if not is_memory and not C.children:
            # If a register addressBlock has no children, skip it
            return None

        return C

    #---------------------------------------------------------------------------
    def parse_registerFile(self, registerFile: minidom.Element) -> comp.Regfile:
        """
        Parses an registerFile and returns an instantiated regfile component
        """
        # Schema:
        #   {nameGroup}
        #       name (required) --> inst_name
        #       displayName --> prop:name
        #       description --> prop:desc
        #   accessHandles
        #   isPresent --> prop:ispresent
        #   dim --> dimensions
        #   addressOffset (required)
        #   {registerFileDefinitionGroup}
        #       typeIdentifier
        #       range (required)
        #       {registerData}
        #           register --> children
        #           registerFile --> children
        #   parameters
        #   vendorExtensions

        d = self.flatten_element_values(registerFile)

        # Check for required values
        required = {'name', 'addressOffset', 'range'}
        missing = required - set(d.keys())
        for m in missing:
            self.msg.fatal("registerFile is missing required tag '%s'" % m, self.src_ref)

        # Create component instance
        if 'dim' in d:
            # is array
            C = self.instantiate_regfile(
                self.create_regfile_definition(),
                d['name'], self.AU_to_bytes(d['addressOffset']),
                d['dim'], self.AU_to_bytes(d['range'])
            )
        else:
            C = self.instantiate_regfile(
                self.create_regfile_definition(),
                d['name'], self.AU_to_bytes(d['addressOffset'])
            )

        # Collect properties and other values
        if 'displayName' in d:
            self.assign_property(C, "name", d['displayName'])

        if 'description' in d:
            self.assign_property(C, "desc", d['description'])

        if 'isPresent' in d:
            self.assign_property(C, "ispresent", d['isPresent'])

        # collect children
        for child_el in d['child_els']:
            if child_el.localName == "register":
                R = self.parse_register(child_el)
                if R:
                    self.add_child(C, R)
            elif child_el.localName == "registerFile":
                R = self.parse_registerFile(child_el)
                if R:
                    self.add_child(C, R)
            else:
                self.msg.error(
                    "Invalid child element <%s> found in <%s:registerFile>"
                    % (child_el.tagName, self.ns),
                    self.src_ref
                )

        if 'vendorExtensions' in d:
            C = self.registerFile_vendorExtensions(d['vendorExtensions'], C)

        if not C.children:
            # Register File contains no fields! RDL does not allow this. Discard
            self.msg.warning(
                "Discarding registerFile '%s' because it does not contain any children"
                % (C.inst_name),
                self.src_ref
            )
            return None

        return C

    #---------------------------------------------------------------------------
    def parse_register(self, register: minidom.Element) -> comp.Reg:
        """
        Parses a register and returns an instantiated reg component
        """
        # Schema:
        #   {nameGroup}
        #       name (required) --> inst_name
        #       displayName --> prop:name
        #       description --> prop:desc
        #   accessHandles
        #   isPresent --> prop:ispresent
        #   dim --> dimensions
        #   addressOffset (required)
        #   {registerDefinitionGroup}
        #       typeIdentifier
        #       size (required)
        #       volatile
        #       access
        #       reset { <<1685-2009>>
        #           value
        #           mask
        #       }
        #       field...
        #   alternateRegisters
        #   parameters
        #   vendorExtensions

        d = self.flatten_element_values(register)

        # Check for required values
        required = {'name', 'addressOffset', 'size'}
        missing = required - set(d.keys())
        for m in missing:
            self.msg.fatal("register is missing required tag '%s'" % m, self.src_ref)

        # Create component instance
        if 'dim' in d:
            # is array
            C = self.instantiate_reg(
                self.create_reg_definition(),
                d['name'], self.AU_to_bytes(d['addressOffset']),
                d['dim'], d['size'] // 8
            )
        else:
            C = self.instantiate_reg(
                self.create_reg_definition(),
                d['name'], self.AU_to_bytes(d['addressOffset'])
            )

        # Collect properties and other values
        if 'displayName' in d:
            self.assign_property(C, "name", d['displayName'])

        if 'description' in d:
            self.assign_property(C, "desc", d['description'])

        if 'isPresent' in d:
            self.assign_property(C, "ispresent", d['isPresent'])

        self.assign_property(C, "regwidth", d['size'])


        reg_access = d.get('access', self._current_addressBlock_access)
        reg_reset_value = d.get('reset.value', None)
        reg_reset_mask = d.get('reset.mask', None)

        # collect children
        for child_el in d['child_els']:
            if child_el.localName == "field":
                field = self.parse_field(child_el, reg_access, reg_reset_value, reg_reset_mask)
                if field is not None:
                    self.add_child(C, field)
            else:
                self.msg.error(
                    "Invalid child element <%s> found in <%s:register>"
                    % (child_el.tagName, self.ns),
                    self.src_ref
                )

        if 'vendorExtensions' in d:
            C = self.register_vendorExtensions(d['vendorExtensions'], C)

        if not C.children:
            # Register contains no fields! RDL does not allow this. Discard
            self.msg.warning(
                "Discarding register '%s' because it does not contain any fields"
                % (C.inst_name),
                self.src_ref
            )
            return None

        return C

    #---------------------------------------------------------------------------
    def parse_field(self, field: minidom.Element, reg_access: rdltypes.AccessType, reg_reset_value: Optional[int], reg_reset_mask: Optional[int]) -> comp.Field:
        """
        Parses an field and returns an instantiated field component
        """
        # Schema:
        #   {nameGroup}
        #       name (required) --> inst_name
        #       displayName --> prop:name
        #       description --> prop:desc
        #   accessHandles
        #   isPresent --> prop:ispresent
        #   bitOffset (required)
        #   resets { <<1685-2014>>
        #       reset {
        #           value
        #           mask
        #       }
        #   }
        #   {fieldDefinitionGroup}
        #       typeIdentifier
        #       bitWidth (required)
        #       {fieldData}
        #           volatile
        #           access
        #           enumeratedValues...
        #           modifiedWriteValue
        #           writeValueConstraint
        #           readAction
        #           testable
        #           reserved
        #   parameters
        #   vendorExtensions

        d = self.flatten_element_values(field)

        # Check for required values
        required = {'name', 'bitOffset', 'bitWidth'}
        missing = required - set(d.keys())
        for m in missing:
            self.msg.fatal("field is missing required tag '%s'" % m, self.src_ref)

        # Discard field if it is reserved
        if d.get('reserved', False):
            return None

        # Create component instance
        C = self.instantiate_field(
            self.create_field_definition(),
            d['name'], d['bitOffset'], d['bitWidth']
        )

        # Collect properties and other values
        if 'displayName' in d:
            self.assign_property(C, "name", d['displayName'])

        if 'description' in d:
            self.assign_property(C, "desc", d['description'])

        if 'isPresent' in d:
            self.assign_property(C, "ispresent", d['isPresent'])

        if 'access' in d:
            self.assign_property(C, "sw", d['access'])
        else:
            self.assign_property(C, "sw", reg_access)

        if 'testable' in d:
            self.assign_property(C, "donttest", not d['testable'])

        if 'reset.value' in d:
            self.assign_property(C, "reset", d['reset.value'])
        elif reg_reset_value is not None:
            mask = (1 << C.width) - 1
            rst = (reg_reset_value >> C.lsb) & mask

            if reg_reset_mask is None:
                rmask = mask
            else:
                rmask = (reg_reset_mask >> C.lsb) & mask

            if rmask:
                self.assign_property(C, "reset", rst)

        if 'readAction' in d:
            self.assign_property(C, "onread", d['readAction'])

        if 'modifiedWriteValue' in d:
            self.assign_property(C, "onwrite", d['modifiedWriteValue'])

        if 'enum_el' in d:
            enum_type = self.parse_enumeratedValues(d['enum_el'], C.inst_name + "_enum_t")
            self.assign_property(C, "encode", enum_type)

        if 'vendorExtensions' in d:
            C = self.field_vendorExtensions(d['vendorExtensions'], C)

        return C

    #---------------------------------------------------------------------------
    def parse_integer(self, s: str) -> int:
        """
        Converts an IP-XACT number string into an int

        IP-XACT technically supports integer expressions in these fields.
        For now, I don't have a compelling reason to support them.

        Handles the following formats:
            - Normal decimal: 123, -456
            - Verilog-style: 'b10, 'o77, d123, 'hff, 8'hff
            - scaledInteger:
                - May have # or 0x prefix for hex
                - May have K, M, G, or T multiplier suffix
        """
        s = s.strip()

        multiplier = {
            "K": 1024,
            "M": 1024*1024,
            "G": 1024*1024*1024,
            "T": 1024*1024*1024*1024
        }

        m = re.fullmatch(r'(-?\d+)(K|M|G|T)?', s, re.I)
        if m:
            v = int(m.group(1))
            if m.group(2):
                v *= multiplier[m.group(2).upper()]
            return v

        m = re.fullmatch(r"\d*'h([0-9a-f]+)", s, re.I)
        if m:
            return int(m.group(1), 16)

        m = re.fullmatch(r"(-)?(0x|#)([0-9a-f]+)(K|M|G|T)?", s, re.I)
        if m:
            v = int(m.group(3), 16)
            if m.group(1):
                v = -v
            if m.group(4):
                v *= multiplier[m.group(4).upper()]
            return v

        m = re.fullmatch(r"\d*'d([0-9]+)", s, re.I)
        if m:
            return int(m.group(1), 10)

        m = re.fullmatch(r"\d*'b([0-1]+)", s, re.I)
        if m:
            return int(m.group(1), 2)

        m = re.fullmatch(r"\d*'o([0-7]+)", s, re.I)
        if m:
            return int(m.group(1), 8)

        raise ValueError

    #---------------------------------------------------------------------------
    def parse_boolean(self, s: str) -> bool:
        """
        Converts several boolean-ish representations to a true bool.
        """
        s = s.lower().strip()
        if s in ("true", "1"):
            return True
        elif s in ("false", "0"):
            return False
        else:
            raise ValueError("Unable to parse boolean value '%s'" % s)

    #---------------------------------------------------------------------------
    def flatten_element_values(self, el: minidom.Element) -> Dict[str, Any]:
        """
        Given any of the IP-XACT RAL component elements, flatten the
        key/value tags into a dictionary.

        Handles values contained in:
            addressBlock, register, registerFile, field

        Ignores several tags that are not interesting to the RAL importer
        """

        d = {
            'child_els' : []
        } # type: Dict[str, Any]

        for child in self.iterelements(el):
            if child.localName == "name":
                # Sanitize name
                d[child.localName] = re.sub(
                    r'[:\-.]',
                    "_",
                    get_text(child).strip()
                )

            elif child.localName in ("displayName", "usage"):
                # Copy string types directly, but stripped
                d[child.localName] = get_text(child).strip()

            elif child.localName == "description":
                # Copy description string types unmodified
                d[child.localName] = get_text(child)

            elif child.localName in ("baseAddress", "addressOffset", "range", "width", "size", "bitOffset", "bitWidth"):
                # Parse integer types
                d[child.localName] = self.parse_integer(get_text(child))

            elif child.localName in ("isPresent", "volatile", "testable", "reserved"):
                # Parse boolean types
                d[child.localName] = self.parse_boolean(get_text(child))

            elif child.localName in ("register", "registerFile", "field"):
                # Child elements that need to be parsed elsewhere
                d['child_els'].append(child)

            elif child.localName in ("reset", "resets"):
                if child.localName == "resets":
                    # pick the first reset
                    reset = self.get_first_child_by_tag(child, self.ns + ":reset")
                    if reset is None:
                        continue
                else:
                    reset = child

                value_el = self.get_first_child_by_tag(reset, self.ns + ":value")
                if value_el:
                    d['reset.value'] = self.parse_integer(get_text(value_el))

                mask_el = self.get_first_child_by_tag(reset, self.ns + ":mask")
                if mask_el:
                    d['reset.mask'] = self.parse_integer(get_text(mask_el))

            elif child.localName == "access":
                s = get_text(child).strip()
                sw = typemaps.sw_from_access(s)
                if sw is None:
                    self.msg.error(
                        "Invalid value '%s' found in <%s>" % (s, child.tagName),
                        self.src_ref
                    )
                else:
                    d['access'] = sw

            elif child.localName == "dim":
                # Accumulate array dimensions
                dim = self.parse_integer(get_text(child))
                if 'dim' in d:
                    d['dim'].append(dim)
                else:
                    d['dim'] = [dim]

            elif child.localName == "readAction":
                s = get_text(child).strip()
                onread = typemaps.onread_from_readaction(s)
                if onread is None:
                    self.msg.error(
                        "Invalid value '%s' found in <%s>" % (s, child.tagName),
                        self.src_ref
                    )
                else:
                    d['readAction'] = onread

            elif child.localName == "modifiedWriteValue":
                s = get_text(child).strip()
                onwrite = typemaps.onwrite_from_mwv(s)
                if onwrite is None:
                    self.msg.error(
                        "Invalid value '%s' found in <%s>" % (s, child.tagName),
                        self.src_ref
                    )
                else:
                    d['modifiedWriteValue'] = onwrite

            elif child.localName == "enumeratedValues":
                # Deal with this later
                d['enum_el'] = child

            elif child.localName == "vendorExtensions":
                # Deal with this later
                d['vendorExtensions'] = child

        return d

    #---------------------------------------------------------------------------
    def parse_enumeratedValues(self, enumeratedValues: minidom.Element, type_name: str) -> Type[rdltypes.UserEnum]:
        """
        Parses an enumeration listing and returns the user-defined enum type
        """
        entries = OrderedDict()
        for enumeratedValue in self.iterelements(enumeratedValues):
            if enumeratedValue.localName != "enumeratedValue":
                continue

            # Flatten element values
            d = {} # type: Dict[str, Any]
            for child in self.iterelements(enumeratedValue):
                if child.localName in ("name", "displayName"):
                    d[child.localName] = get_text(child).strip()
                elif child.localName == "description":
                    d[child.localName] = get_text(child)
                elif child.localName == "value":
                    d[child.localName] = self.parse_integer(get_text(child))

            # Check for required values
            required = {'name', 'value'}
            missing = required - set(d.keys())
            for m in missing:
                self.msg.fatal("enumeratedValue is missing required tag '%s'" % m, self.src_ref)

            entry_name = d['name']
            entry_value = d['value']
            displayname = d.get('displayName', None)
            desc = d.get('description', None)

            entries[entry_name] = (entry_value, displayname, desc)

        enum_type = rdltypes.UserEnum(type_name, entries) #pylint: disable=no-value-for-parameter

        return enum_type

    #---------------------------------------------------------------------------
    @staticmethod
    def get_children_by_tag(el: minidom.Element, tag: str) -> List[minidom.Element]:
        # Returns a list of immediate children that match the full tag
        c = []
        for child in el.childNodes:
            if isinstance(child, minidom.Element) and (child.tagName == tag):
                c.append(child)
        return c

    #---------------------------------------------------------------------------
    @staticmethod
    def get_first_child_by_tag(el: minidom.Element, tag: str) -> Optional[minidom.Element]:
        # Returns the first child that matches the full tag
        for child in el.childNodes:
            if isinstance(child, minidom.Element) and (child.tagName == tag):
                return child
        return None

    #---------------------------------------------------------------------------
    def iterelements(self, el: minidom.Element) -> Iterable[minidom.Element]:
        for child in el.childNodes:
            if not isinstance(child, minidom.Element):
                continue
            if child.prefix != self.ns:
                continue
            yield child

    #---------------------------------------------------------------------------
    def AU_to_bytes(self, au: int) -> int:
        """
        IP-XACT addresses are byte-agnostic and express addresses and ranges as
        'addressable units' that each span addressUnitBits bits.
        This function converts the AUs into normalized bytes.

        To make my life easier, this importer only allows multiples of 8 for
        the addressUnitBits property.
        """
        bit_units = au * self._addressUnitBits
        byte_units = bit_units // 8
        return byte_units

    #---------------------------------------------------------------------------
    def addressBlock_vendorExtensions(self, vendorExtensions: minidom.Element, component: comp.Component) -> comp.Component:
        #pylint: disable=unused-argument
        return component

    def registerFile_vendorExtensions(self, vendorExtensions: minidom.Element, component: comp.Component) -> comp.Component:
        #pylint: disable=unused-argument
        return component

    def register_vendorExtensions(self, vendorExtensions: minidom.Element, component: comp.Component) -> comp.Component:
        #pylint: disable=unused-argument
        return component

    def field_vendorExtensions(self, vendorExtensions: minidom.Element, component: comp.Component) -> comp.Component:
        #pylint: disable=unused-argument
        return component

#===============================================================================
def get_text(el: minidom.Element) -> str:
    for child in el.childNodes:
        if isinstance(child, minidom.Text):
            return child.data
    return ""
