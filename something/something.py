import xml.etree.ElementTree as ET
import re

tree = ET.parse('your_file.xml')  # Replace with your XML file
root = tree.getroot()

# Find the fieldMap object
field_map_obj = root.find(".//object[@type='DataModel:fieldMap']")

if field_map_obj is not None:
    # Look for a nested fieldReference object
    for i, ref_obj in enumerate(list(field_map_obj.findall(".//object[@type='DataModel:fieldReference']"))):
        prop = ref_obj.find("property[@name='value']")
        if prop is not None and 'dataSource.layout["source_table_name"]' in prop.attrib.get('value', ''):
            print("✔ Found dataSource.layout fieldReference")

            # Get parent object (likely <property>) and then its parent's children
            parent_object = field_map_obj.getparent() if hasattr(field_map_obj, 'getparent') else root
            siblings = list(parent_object)

            try:
                # Find index of current fieldMap
                field_map_index = siblings.index(field_map_obj)

                # Get the next sibling object
                next_obj = siblings[field_map_index + 1]
                if next_obj.tag == "object" and next_obj.attrib.get("type") == "SQLExpressionPart":
                    # Extract the property value
                    sql_prop = next_obj.find("property[@name='value']")
                    if sql_prop is not None:
                        sql_value = sql_prop.attrib.get('value', '')
                        # Extract values inside the IN(...) clause
                        in_match = re.search(r"IN\s*\(([^)]*)\)", sql_value)
                        if in_match:
                            in_values = [v.strip(" '\"") for v in in_match.group(1).split(',')]
                            print("📥 IN clause values:", in_values)
            except (IndexError, ValueError):
                print("⚠ Could not find next SQLExpressionPart object.")

str_s = "=ARRAYFORMULA(
  BYROW(A:A,
    LAMBDA(row,
      LET(
        txt , REGEXREPLACE(TRIM(row), CHAR(10), " "),          /* 1: normalise new‑lines → spaces */
        parts , FLATTEN(SPLIT(txt, " ")),                      /* 2: one long list of “words”   */
        keep , FILTER(parts, REGEXMATCH(parts, "^[A-Z_]{2,}$")),/*3: only FULLY‑CAP words        */
        IF(keep="", "", TEXTJOIN(" ", TRUE, keep))             /* 4: join them back together    */
      )
    )
  )
)
"
