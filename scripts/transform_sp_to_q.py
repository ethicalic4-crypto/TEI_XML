import sys
import os
import shutil
import logging
import xml.etree.ElementTree as ET

def backup_file(path):
    if os.path.exists(path):
        shutil.copy2(path, path + '.bak')
        logging.info(f"백업 생성: {path}.bak")

def move_particDesc_to_profileDesc(root, ns):
    teiHeader = root.find('tei:teiHeader', ns)
    if teiHeader is None:
        return
    particDesc = teiHeader.find('tei:particDesc', ns)
    profileDesc = teiHeader.find('tei:profileDesc', ns)
    if particDesc is not None:
        if profileDesc is None:
            profileDesc = ET.SubElement(teiHeader, 'profileDesc')
        for child in list(particDesc):
            profileDesc.append(child)
        teiHeader.remove(particDesc)

def standardize_header_order(root, ns):
    teiHeader = root.find('tei:teiHeader', ns)
    if teiHeader is None:
        return
    # 표준 순서: fileDesc, profileDesc, revisionDesc
    children = list(teiHeader)
    order = ['fileDesc', 'profileDesc', 'revisionDesc']
    sorted_children = []
    for tag in order:
        for c in children:
            if c.tag.endswith(tag):
                sorted_children.append(c)
    for c in children:
        if c not in sorted_children:
            sorted_children.append(c)
    teiHeader[:] = sorted_children

def transform_sp_to_q(root, ns):
    for body in root.findall('.//tei:body', ns):
        for sp in list(body.findall('.//tei:sp', ns)):
            who = sp.attrib.get('who')
            q = ET.Element('q')
            if who:
                q.attrib['who'] = who
            # ptr, speaker, p 등 내부 구조 보존
            for child in list(sp):
                if child.tag.endswith('p'):
                    p = ET.Element('p')
                    p.text = child.text
                    q.append(p)
                else:
                    q.append(child)
            body.insert(list(body).index(sp), q)
            body.remove(sp)

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
    if len(sys.argv) < 2:
        print("사용법: python transform_sp_to_q.py <input.xml>")
        sys.exit(1)
    input_path = sys.argv[1]
    output_path = 'test_tei_final.xml'
    backup_file(output_path)
    tree = ET.parse(input_path)
    root = tree.getroot()
    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
    move_particDesc_to_profileDesc(root, ns)
    standardize_header_order(root, ns)
    transform_sp_to_q(root, ns)
    tree.write(output_path, encoding='utf-8', xml_declaration=True)
    logging.info(f"스키마 변환 완료: {output_path}")

if __name__ == '__main__':
    main()
