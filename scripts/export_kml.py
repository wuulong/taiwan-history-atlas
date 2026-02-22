import sqlite3
import json
import xml.etree.ElementTree as ET

DB_PATH = "data/history_texts/taiwan_history.db"
KML_OUTPUT_PATH = "data/history_texts/Taiwan_History_Geo.kml"

def create_kml_placemark(doc, name, description, lon, lat, color="ff0000ff"): # Default red
    placemark = ET.SubElement(doc, 'Placemark')
    
    name_elem = ET.SubElement(placemark, 'name')
    name_elem.text = name

    desc_elem = ET.SubElement(placemark, 'description')
    desc_elem.text = description

    style = ET.SubElement(placemark, 'Style')
    icon_style = ET.SubElement(style, 'IconStyle')
    color_elem = ET.SubElement(icon_style, 'color')
    color_elem.text = color 
    icon = ET.SubElement(icon_style, 'Icon')
    href = ET.SubElement(icon, 'href')
    href.text = "http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png"

    point = ET.SubElement(placemark, 'Point')
    coords = ET.SubElement(point, 'coordinates')
    coords.text = f"{lon},{lat},0"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT e.name, e.type, s.longitude, s.latitude, s.meta_data, group_concat(m.snippet, ' | ')
        FROM spatial_links s
        JOIN entities e ON s.entity_id = e.id
        LEFT JOIN mentions m ON e.id = m.entity_id
        GROUP BY e.id
    """)
    rows = cursor.fetchall()
    
    print(f"Exporting {len(rows)} spatial points to KML...")

    kml = ET.Element('kml', xmlns="http://www.opengis.net/kml/2.2")
    document = ET.SubElement(kml, 'Document')
    doc_name = ET.SubElement(document, 'name')
    doc_name.text = '臺灣通史 歷史空間實體'
    
    for row in rows:
        name, entity_type, lon, lat, meta_data_str, snippets = row
        
        meta_data = {}
        if meta_data_str:
            try:
                meta_data = json.loads(meta_data_str)
            except json.JSONDecodeError:
                pass
                
        # 決定顏色 (例如基礎建設藍色，地點紅色)
        color = "ffff0000" # 藍色 for Infrastructure
        if entity_type == 'Location':
            color = "ff0000ff" # 紅色
            
        desc_html = f"<b>類型:</b> {entity_type}<br>"
        desc_html += f"<b>來源判定:</b> {meta_data.get('geo_source', '未知')}<br>"
        desc_html += f"<b>錨定地區:</b> {meta_data.get('anchor_used', '無')}<br>"
        desc_html += f"<b>對合地名:</b> {meta_data.get('matched_NAME', '')}<br><br>"
        desc_html += f"<b>《臺灣通史》原文節錄:</b><br>{snippets[:500]}..." if snippets else "無上下文"

        create_kml_placemark(document, name, desc_html, lon, lat, color)

    tree = ET.ElementTree(kml)
    tree.write(KML_OUTPUT_PATH, encoding='utf-8', xml_declaration=True)
    conn.close()
    
    print(f"Successfully generated KML file: {KML_OUTPUT_PATH}")

if __name__ == "__main__":
    main()
